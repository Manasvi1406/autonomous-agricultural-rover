from setuptools import find_packages, setup

package_name = 'agri_rover_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='manasvi',
    maintainer_email='manasvi@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
              'sensor_simulator = agri_rover_sensors.sensor_simulator:main',
              'data_logger = agri_rover_sensors.data_logger:main',
              'nav_status_bridge = agri_rover_sensors.nav_status_bridge:main',
              'yolo_detector = agri_rover_sensors.yolo_detector:main',
        ],
    },
)
