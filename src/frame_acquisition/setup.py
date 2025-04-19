from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'frame_acquisition'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dev',
    maintainer_email='jakubpajak02@outlook.com',
    description='This package is responsible for frame acquisition from the USB camera and basic adjustments on the frame before proper analysis',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [ 
            'acquire_frame = frame_acquisition.acquire_frame:main',
            'process_frame = frame_acquisition.process_frame:main',
            'process_frame_bin = frame_acquisition.process_frame_bin:main',
        ],
    },
)
