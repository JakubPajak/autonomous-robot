from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'line_detection'

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
    maintainer_email='dev@todo.todo',
    description='TODO: Package description',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'acquire_frame = line_detection.acquire_frame:main',
            'process_frame_rgb = line_detection.process_frame_rgb:main',
            'process_frame_nn = line_detection.process_frame_nn:main',
        ],
    },
)
