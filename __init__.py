# coding=utf-8
"""
None
"""
from os.path import dirname
from sys import path

if dirname(__file__) not in path:
    path.append(dirname(__file__))

try:
    from .nglwrapper import NGLWrapper
except:
    from nglwrapper import NGLWrapper

__all__ = ['NGLWrapper']  # type: str
