from conan import ConanFile
from conan.tools.build import cross_building
from six import StringIO


class TestPackage(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        pass # nothing to build, but tests should not warn

    def test(self):
        if cross_building(self):
            return
        output = StringIO()
        self.run('java -version', output, env="conanrun")
        version_info = output.getvalue()
        print(f'output from command was {version_info}')
        if "Zulu" not in version_info:
            raise Exception("java call seems not use the Zulu OpenJDK bin:\n{0}".format(version_info))
