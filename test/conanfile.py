from conans.model.conan_file import ConanFile
from conans import CMake
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "9b"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    requires = "libjpeg/9b@zamazan4ik/stable"

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_dir="../../", build_dir="./")
        cmake.build()

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")

    def test(self):
        self.run("cd bin && .%srdjpgcom -verbose -raw ../../../testimg.jpg" % os.sep)
