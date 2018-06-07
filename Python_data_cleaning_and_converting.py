
# coding: utf-8

# In[1]:

import xml.etree.cElementTree as ET
import pprint


# In[52]:

OSM_FILE = "Sunnyvale_CA.osm" 
SAMPLE_FILE = "Sunnyvale_100sample.osm"


# In[36]:

filename = OSM_FILE


# In[ ]:

# This is part of code provided in lesson 13 to create a file of reduced size
k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# In[40]:

# The followong code is to determine which street names might be candidates to correcting 
# if the word at the end of name is not in the list of values in variable "expected"

from collections import defaultdict
import re

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_cardinals_re = re.compile(r'^[NSEW]\b')

# The variable expected has been updated by me after auditing the xml file
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Terrace", "Circle", "Expressway", "Loop"]

# This variable has been updated by me after auditing the xml file
mapping = { "street": "Street",
            "Rd": "Road",
            "Ave": "Avenue",
           "Blvd": "Boulevard",
           "Dr": "Drive",
           "Common": "Circle",
           "Creek": "Creek Boulevard",
           "Evelyn": "Evelyn Avenue",
          "N": "North",
          "E": "East",
          "W": "West"}    

# The following code has been provided in lesson 13
def audit_street_types(street_types, street_name):
    t = street_type_re.search(street_name)
    c = street_cardinals_re.search(street_name)
    if t and t.group() not in expected:
        street_types[t.group()].add(street_name)
    if c:
        street_types[c.group()].add(street_name)

    
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_field(tag, 'addr:street'):
                    audit_street_types(street_types, tag.attrib['v'])
                    
    osm_file.close()
    return street_types


audit(filename)


# In[41]:

# This function takes as argument a street name to be corrected and modifies only street type
def update_type(name, mapping):
    if street_type_re.search(name):
        
        t = street_type_re.search(name).group()
        
        stpos = street_type_re.search(name).start()
        try: 
            new = mapping[t]
            better_name = name[0:stpos] + new
            
            return better_name
        except:
            
            return name
    else:
        
        return name


# In[42]:

# This function is used in function better_names and takes as argument a street name that has already corrected type.
def update_cardinals(name, mapping):
    if street_cardinals_re.search(name):
        
        c = street_cardinals_re.search(name).group()
        
        endpos = street_cardinals_re.search(name).end()
        try: 
            new = mapping[c]
            better_name = new + name[endpos:] 
            
            return better_name
        except:
            
            return name
    else:
        
        return name


# In[43]:

# This function returns a dictionary of street names to be corrected as keys and corrected name as value.
def better_names():
    st_types = audit(filename)
    better_street_names = defaultdict(set)


    for st_type, ways in st_types.iteritems():
        for name in ways:
            name1 = update_type(name, mapping)
            better_name = update_cardinals(name1, mapping)
            if not better_name == name:
                better_street_names[name] = better_name
    return better_street_names



# In[44]:

# This variable containing a dictionary will be used during data trasfer from xml file to csv file
# Each street name will be compared against all the keys in this dictionary and replaced by a corrected value if 
# it exists.
better_street_names = better_names()
print better_street_names


# In[45]:

import csv
import codecs
import cerberus
import schema


# In[46]:

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')


# In[47]:

# This schema has been provided in lesson 13
SCHEMA = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}


# In[48]:

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# In[49]:

# This function is used to shape ways and nodes tags. It is used if function shape_element.
# This is my code
def shape_tag(ID_, tag, default_tag_type):
    k = tag.attrib['k']
    colon = LOWER_COLON.search(tag.attrib['k'])
    tag_dict = {}
    tag_dict['id'] = ID_
    for key in better_street_names.keys(): # This is a verificaation if a street name has to be corrected
            if tag.attrib['v'] == key:
                tag.attrib['v'] = better_street_names[key] 
    tag_dict['value'] = tag.attrib['v']
    if colon:
        end = k.index(':')
        start = k.index(':') + 1
        tag_dict['type'] = k[0:end]
        tag_dict['key'] = k[start:]
    else:
        tag_dict['key'] = k
        tag_dict['type'] = default_tag_type
        
    return tag_dict


# In[50]:

# This function is used to shape element from xml file returning a dictionary with ways, nodes and tags values.
# This is my code
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    
    
    ID_ = int(element.attrib['id'])
    if element.tag == 'node':
        for key in node_attr_fields:
            if key == 'id' or key == 'uid' or key == 'changeset':
                node_attribs[key] = int(element.attrib[key])
            elif key == 'lat' or key == 'lon':
                node_attribs[key] = float(element.attrib[key])
            else:
                node_attribs[key] = element.attrib[key]
        for tag in element.iter('tag'):
            try: # Any k value containing problematic characters will not be considered
                problem_chars.search(tag.attrib['k'])
                tags.append(shape_tag(ID_, tag, default_tag_type))
            except:
                continue 
        return {'node': node_attribs, 'node_tags': tags}
    
    
    
    elif element.tag == 'way':
        position = 0
        for key in way_attr_fields:
            if key == 'id' or key == 'uid' or key == 'changeset':
                way_attribs[key] = int(element.attrib[key])
            else:
                way_attribs[key] = element.attrib[key]
        for tag in element.iter():
            
            if tag.tag == 'tag':
                try: # Any k value containing problematic characters will not be considered
                    problem_chars.search(tag.attrib['k'])
                    tags.append(shape_tag(ID_, tag, default_tag_type))
                except:
                    
                    continue
                    
                    
                
            elif tag.tag == 'nd':
                way_nodes_dict = {}
                way_nodes_dict['id'] = ID_
                way_nodes_dict['node_id'] = int(tag.attrib['ref'])
                way_nodes_dict['position'] = position
                position += 1
                way_nodes.append(way_nodes_dict)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# In[51]:

# ================================================== #
#               Helper Functions 
# This code has been provided in lesson 13
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        print 'Test'
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[31]:

# ================================================== #
#               Main Function                        #
#  This code has been provided in lesson 13          #
# The only modification I made is change mode in     # 
# which csv file is opened from 'w' to binary 'wb'   #
# See comments in Project Report.                    #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

# I changed the mode from 'w' to 'wb'. This would avoid creation of empty line in csv file

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \           
         codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \  
         codecs.open(WAYS_PATH, 'wb') as ways_file, \             
         codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    
    process_map(SAMPLE_FILE, validate=True)


# In[ ]:



