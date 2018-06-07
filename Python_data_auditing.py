
# coding: utf-8

# In[5]:

import xml.etree.cElementTree as ET
import pprint


# In[6]:

OSM_FILE = "Sunnyvale_CA.osm"  
filename = OSM_FILE


# In[7]:

# This function counts number of occurencies per tag
# This is my code from exercise in lesson 13

def count_tags(filename):
        tags = {}
        
        for event, elem in ET.iterparse(filename):
            if elem.tag in tags.keys():
                tags[elem.tag] += 1
            else:
                tags[elem.tag] = 1
            
        return tags
tags = count_tags(filename)
pprint.pprint(tags)


# In[8]:

# This code is my code from exercise in lesson 13
# This function creates a set of unique users. By determining its length we know the number of unique users
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        for a in element.attrib:
            if a == 'uid':
                users.add(element.attrib['uid'])
        
    return users

users = process_map(filename)
pprint.pprint(len(users))


# In[9]:

# This function creates a dictionary with unique k values and count of their occurencies. This is my code.
def get_kvalues(filename):
    k_values = {}
    for event, element in ET.iterparse(filename, events = ('start',)):
        for tag in element.iter('tag'):
            if tag.attrib['k'] in k_values.keys():
                k_values[tag.attrib['k']] += 1
            else:
                k_values[tag.attrib['k']] = 1
    return k_values

k_values = get_kvalues(filename)
pprint.pprint(k_values)


# In[11]:

# This function determines if a value in k field is the value we are looking for
# Arguments are element from xml file and a string with the name of field we are interested in. This is my code.

def is_field(elem, field):
    return (elem.attrib['k'] == field)


# In[12]:

# This function returns a set of unique values in a field. This is my code.
def get_field_values(filename, field):
    values = set()
    for event, element in ET.iterparse(filename, events = ('start',)):
        for tag in element.iter('tag'):
            if is_field(tag, field):
                values.add(tag.attrib['v'])
        
    return values


# In[13]:

# This is a list of unique streets in xml file.
streets = get_field_values(filename, 'addr:street')
pprint.pprint(len(streets))
pprint.pprint(streets)


# In[14]:

# This is a list of unique postcodes in xml file
postcodes = get_field_values(filename, 'addr:postcode')
pprint.pprint(len(postcodes))
pprint.pprint(postcodes)


# In[15]:

# This is a list of unique cities' names in xml file
cities = get_field_values(filename, 'addr:city')
pprint.pprint(len(cities))
print(cities)


# In[ ]:



