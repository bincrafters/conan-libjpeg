#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class libjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    version = "9b"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    license = "https://sourceforge.net/projects/libjpeg"
    url = "http://github.com/bincrafters/conan-libjpeg"
    install = "libjpeg-install"
    exports_sources = ['Win32.Mak']

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        # file name examples:  linux jpegsrc.v9b.tar.gz,  windows jpegsr9b.zip
        download_url_base = "http://ijg.org/files/"
        archive_prefix = "jpegsr" if self.settings.os == "Windows" else "jpegsrc.v"
        archive_ext = ".zip" if self.settings.os == "Windows" else ".tar.gz"
        download_url = download_url_base + archive_prefix + self.version + archive_ext
        self.output.info("trying download of url: " + download_url)
        tools.get(download_url)
        os.rename("jpeg-" + self.version, "sources")
        if self.settings.compiler == 'Visual Studio':
            shutil.copy('Win32.Mak', os.path.join('sources', 'Win32.Mak'))
            shutil.copy(os.path.join('sources', 'jconfig.vc'), os.path.join('sources', 'jconfig.h'))

    def build_nmake(self):
        with tools.chdir("sources"):
            vcvars_command = tools.vcvars_command(self.settings)
            self.run('%s && nmake -f makefile.vc' % vcvars_command)

    def build_configure(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        config_args = []
        if self.options.shared:
            config_args.append("--enable-shared=yes --enable-static=no")
        else:
            config_args.append("--enable-shared=no --enable-static=yes")
        prefix = os.path.abspath(self.install)
        config_args.append("--prefix=%s" % prefix)

        env_build.configure("sources", args=config_args, build=False, host=False, target=False)
        env_build.make()
        env_build.make(args=["install"])

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_nmake()
        else:
            self.build_configure()

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="libjpeg.lib", dst="lib", src="sources", keep_path=False)
            for filename in ['jpeglib.h', ' jerror.h', 'jconfig.h', 'jmorecfg.h']:
                self.copy(pattern=filename, dst="include", src="sources")
        else:
            self.copy("*.h", dst="include", src=os.path.join(self.install, "include"), keep_path=True)
            self.copy(pattern="*.so", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install, "lib"), keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ['libjpeg']
        else:
            self.cpp_info.libs = ['jpeg']
