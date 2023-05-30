#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform

from conan import ConanFile
from conan.tools.files import get

from conan.tools.files import save, load

from conan.tools.layout import basic_layout
from conan.tools.files import copy

from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import unix_path, VCVars, is_msvc

from conan.errors import ConanInvalidConfiguration
from conan.errors import ConanException



class ZuluOpenJDKConan(ConanFile):
    name = 'java_installer'
    url = 'https://github.com/datalogics/conan-java_installer'
    description = 'Java installer distributed via Conan'
    license = 'https://azul.com'
    topics = ("java", "jdk", "openjdk")
    settings = 'os', 'arch'

    @property
    def _jni_folder(self):
        folder = {'Linux': 'linux',
                  'Macos': 'darwin',
                  'Windows': 'win32',
                  'AIX': 'aix',
                  'SunOS': 'solaris'}.get(str(self.settings.os))
        return os.path.join('include', folder)

    @property
    def _binary_key(self):
        return '{0}_{1}'.format(self.settings.os, self.settings.arch)

    @property
    def layout(self):
       basic_layout(self, src_folder="source")

    def source(self):
        data = get(self, **self.conan_data["binaries"][self.version].get(self._binary_key, None), strip_root=True)
        if data is None:
            raise ConanInvalidConfiguration("Unsupported Architecture.  No data was found in {0} for OS "
                                            "{1} with arch {2}".format(self.version, self.settings.os,
                                                                       self.settings.arch))
        if self.settings.os == 'Macos' and self.settings.arch == 'x86':
            raise ConanInvalidConfiguration(
                'Unsupported System (32-bit Mac OS X)')

    def build(self):
        self.output.info('Downloading {0}'.format(
            self.conan_data["binaries"][self.version][self._binary_key].get('url')))
        tools.get(**self.conan_data["binaries"][self.version][self._binary_key],
                  destination=self.layout, strip_root=True)

    def package(self):
        self.copy(pattern='*', dst='.', src=self.layout)
        copy(self, "*", self.source_folder, self.package_folder, keep_path=False)

    def package_id(self):
        del self.info.settings.os.subsystem

    def package_info(self):
        self.cpp_info.includedirs.append(self._jni_folder)
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.libdirs = []
        java_home = self.package_folder
        self.output.info(
            'Creating JAVA_HOME environment variable with : {0}'.format(java_home))
        self.env_info.JAVA_HOME = java_home
        bin_path = os.path.join(java_home, 'bin')
        self.output.info(
            'Prepending PATH environment variable with : {0}'.format(bin_path))
        self.env_info.PATH.append(bin_path)
