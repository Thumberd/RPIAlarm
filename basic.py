#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import time


def CPrint(text):
	actualTime = time.strftime("[%d/%m/%Y] %H:%M:%S -- ")
	print(actualTime + text)
