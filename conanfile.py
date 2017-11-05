import os
import shutil

from conans import ConanFile, CMake, AutoToolsBuildEnvironment
from conans.client import tools
from conans.util import files

class libjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files. It was developed by Tom Lane and the Independent JPEG Group (IJG) during the 1990's and it is now maintained by several developers using various services identified in the SourceForge summary."
    version = "9b"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    license = "GNU General Public License version 2.0 (GPLv2): https://sourceforge.net/projects/libjpeg/"
    exports = "CMakeLists.txt", "libjpeg/*", "CMakeListsJPEG.txt"
    url="http://github.com/ZaMaZaN4iK/conan-libjpeg"
    # requires ="zlib/1.2.8@lasote/stable"

    LIBJPEG_FOLDER_NAME = "jpeg-%s" % version
    src_name = "jpegsr%s.zip" % version
    download_url = "http://ijg.org/files/%s" % src_name

    def requirements(self):
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

    def remove_crlf(self, filename):
        with tools.chdir(self.LIBJPEG_FOLDER_NAME):
            self.run("mv ./%s ./%s_win" % (filename, filename))
            self.run("tr -d '\015' <./%s_win >./%s" % (filename, filename))
            os.unlink("./%s_win" % filename)

    def source(self):
        tools.download(self.download_url, self.src_name)
        tools.unzip(self.src_name)
        shutil.copy("CMakeListsJPEG.txt", "%s/CMakeLists.txt" % (self.LIBJPEG_FOLDER_NAME))
        #os.unlink(self.src_name)
        if self.settings.os != "Windows":
            # Remove Windows-like line endings (CRLF) from build scripts
            for filename in ["configure", "aclocal.m4", "configure.ac", "Makefile.am", "config.sub", "ltmain.sh", "Makefile.in", "depcomp", "config.guess", "missing"]:
                self.remove_crlf(filename)
            self.run("chmod +x ./%s/configure" % self.LIBJPEG_FOLDER_NAME)

    def build(self):
        with tools.chdir(self.LIBJPEG_FOLDER_NAME):
            if not tools.OSInfo().is_windows:
                env_build = AutoToolsBuildEnvironment(self)
                env_build.fpic = True
                confArgs = []
                if self.options.shared:
                    confArgs.append("--enable-shared=yes --enable-static=no")
                else:
                    confArgs.append("--enable-shared=no --enable-static=yes")


                env_build.configure("./", args=confArgs, build=False, host=False, target=False)
                env_build.make()
            else:
                files.mkdir("_build")
                with tools.chdir("_build"):
                    cmake = CMake(self)
                    cmake.configure(build_dir=".")
                    cmake.build(build_dir=".")

    def package(self):
        """ Define your conan structure: headers, libs, bins and data. After building your
            project, this method is called to create a defined structure:
        """
        # Copying header files
        self.copy("*.h", "include", "%s" % (self.LIBJPEG_FOLDER_NAME), keep_path=False)
        self.copy("*.h", "include", "%s" % ("_build"), keep_path=False)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            self.copy(pattern="libjpeg.lib", dst="lib", src="build/lib", keep_path=False)
            self.copy(pattern="libjpeg.lib", dst="lib", src="build/lib", keep_path=False)
        else:
            self.copy(pattern="*.so", dst="lib", src="%s/.libs" % self.LIBJPEG_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.a", dst="lib", src="%s/.libs" % self.LIBJPEG_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['libjpegd']
            else:
                self.cpp_info.libs = ['libjpeg']
        else:
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['jpeg']
            else:
                self.cpp_info.libs = ['jpeg']
