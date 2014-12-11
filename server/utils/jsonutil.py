#!/usr/bin/env python
# coding: utf-8

''' define json utils '''

def dbobject2dict(dbobject, *keys):
	result = {}
	for key in keys:
		value = dbobject.get(key)
		if value != None:
			result[key] = value
	return result

def cursor2list(cursor, *keys):
	result = []
	for dbobject in cursor:
		result.append(dbobject2dict(dbobject, *keys))
	return result
