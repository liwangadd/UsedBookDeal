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
		d = {}
		for key in keys:
			value = dbobject.get(key)
			if value != None:
				if key == 'imgs':
					d['img'] = value[0]
				else:
					d[key] = value
		result.append(d)
	return result
