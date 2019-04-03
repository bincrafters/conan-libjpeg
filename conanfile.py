#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibjpegConan(ConanFile):
    name = "libjpeg"
    version = "9b"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "http://github.com/bincrafters/conan-libjpeg"
    license = "BSD"
    homepage = "http://ijg.org"
    topics = ("conan", "libjpeg", "jpeg", "image-writer", "image-reader")
    author = "Bincrafters <bincrafters@gmail.com>"
    exports = ["LICENSE.md"]
    exports_sources = ["Win32.Mak"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        sha256 = "240fd398da741669bf3c90366f58452ea59041cacc741a489b99f2f6a0bad052"
        tools.get("{}/files/jpegsrc.v{}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        os.rename("jpeg-" + self.version, self._source_subfolder)

    def _build_nmake(self):
        if self.settings.compiler == 'Visual Studio':
            shutil.copy('Win32.Mak', os.path.join(self._source_subfolder, 'Win32.Mak'))
        with tools.chdir(self._source_subfolder):
            shutil.copy('jconfig.vc', 'jconfig.h')
            vcvars_command = tools.vcvars_command(self.settings)
            params = "nodebug=1" if self.settings.build_type == 'Release' else ""
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if self.settings.compiler.runtime in ["MD", "MDd"]:
                tools.replace_in_file('makefile.vc', '(cvars)', '(cvarsdll)')
                tools.replace_in_file('makefile.vc', '(conlibs)', '(conlibsdll)')
            else:
                tools.replace_in_file('makefile.vc', '(cvars)', '(cvarsmt)')
                tools.replace_in_file('makefile.vc', '(conlibs)', '(conlibsmt)')
            self.run('%s && nmake -f makefile.vc %s libjpeg.lib' % (vcvars_command, params))

    def _build_configure(self):
        # works for unix and mingw environments
        env_build = AutoToolsBuildEnvironment(self, win_bash=self.settings.os == 'Windows')
        config_args = []
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])
        prefix = os.path.abspath(self.package_folder)
        if self.settings.os == 'Windows':
            prefix = tools.unix_path(prefix)
        config_args.append("--prefix=%s" % prefix)

        # mingw-specific
        if self.settings.os == 'Windows':
            if self.settings.arch == "x86_64":
                config_args.append('--build=x86_64-w64-mingw32')
                config_args.append('--host=x86_64-w64-mingw32')
            if self.settings.arch == "x86":
                config_args.append('--build=i686-w64-mingw32')
                config_args.append('--host=i686-w64-mingw32')

        env_build.configure(configure_dir=self._source_subfolder, args=config_args)
        env_build.make()
        env_build.make(args=["install"])

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_nmake()
        else:
            self._build_configure()

    def package(self):
        self.copy("README", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self.settings.compiler == "Visual Studio":
            for filename in ['jpeglib.h', 'jerror.h', 'jconfig.h', 'jmorecfg.h']:
                self.copy(pattern=filename, dst="include", src=self._source_subfolder, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
        shutil.rmtree(os.path.join(self.package_folder, 'share'), ignore_errors=True)
        # can safely drop bin/ because there are no shared builds
        shutil.rmtree(os.path.join(self.package_folder, 'bin'), ignore_errors=True)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ['libjpeg']
        else:
            self.cpp_info.libs = ['jpeg']
