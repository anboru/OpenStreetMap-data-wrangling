
# coding: utf-8

# In[28]:

import sqlite3
import pprint
db = sqlite3.connect("C:\Users\Anna\sqlite-windows\sqlite_windows\Project3.db")
c = db.cursor()


# In[29]:

# Fix street names containing house numbers.

#1. Select all records with these id's to verify that these ways and nodes tags 
#do not have records with house number alone.
query = '''
select * from nodes_tags
where id in (select id from nodes_tags
where value in ('1296 Kifer Road', '10130 Bubb Road', '3001 Oakmead Village Drive'));
'''
c.execute(query)
rows = c.fetchall()
print "Nodes_tags"
pprint.pprint(rows)

query = '''
select * from ways_tags
where id in (select id from ways_tags
where value in ('1296 Kifer Road', '10130 Bubb Road', '3001 Oakmead Village Drive'));
'''
c.execute(query)
rows = c.fetchall()
print "Ways_tags"
pprint.pprint(rows)


# In[31]:

#2. Insert new records with house number alone
query = '''
insert into ways_tags
select id, 'housenumber_1', substr(value, 1, instr(value, ' ') - 1), 'addr'
from ways_tags
where id in (select distinct id from ways_tags 
where value in ('1296 Kifer Road', '10130 Bubb Road', '3001 Oakmead Village Drive')) 
and key = 'street';
'''
c.execute(query)

query = '''
insert into nodes_tags
select id, 'housenumber_1', substr(value, 1, instr(value, ' ') - 1), 'addr'
from nodes_tags
where id in (select distinct id from nodes_tags 
where value in ('1296 Kifer Road', '10130 Bubb Road', '3001 Oakmead Village Drive')) 
and key = 'street';
'''
c.execute(query)

#3 Update street names to remove house number from name.

query = '''
update ways_tags
set value = substr(value, instr(value, ' ') + 1)
where id in (select distinct id from ways_tags 
where value in ('1296 Kifer Road', '10130 Bubb Road', '3001 Oakmead Village Drive'))
and key = 'street';
'''
c.execute(query)

query = '''
update nodes_tags
set value = substr(value, instr(value, ' ') + 1)
where id in (select distinct id from nodes_tags 
where value in ('1296 Kifer Road', '10130 Bubb Road', '3001 Oakmead Village Drive'))
and key = 'street';
'''
c.execute(query)


# In[32]:

#4. Select all records with these id's to verify that update and insert were successfull.
query = '''
select * from ways_tags
where id in (95614488, 205805506)
order by id;
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)

query = '''
select * from nodes_tags
where id in (2574503939);
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[33]:

# Fix inaccurate postal codes
# Select all tags describing ways or nodes with inaccurate postal codes.

query = '''
select * from ways_tags where id in (select id from ways_tags 
where value in ('94807', '95914', '9404')) order by id;
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)

query = '''
select * from nodes_tags where id in (select id from nodes_tags 
where value in ('94807', '95914', '9404')) order by id;
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[34]:

# Fix zip codes strarting with state CA
query = '''
select * from ways_tags
where key = 'postcode'
and substr(value, 1, 2) = 'CA';
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)

query = '''
update ways_tags
set value = substr(value, 4)
where key = 'postcode'
and substr(value, 1, 2) = 'CA';
'''
c.execute(query)


# In[35]:

# Update tables ways_tags and nodes_tags replacing incorrect values of postal codes.
# Table fixed_postal_codes is described in main Project report.

query = '''
update ways_tags
set value =
(select A.new_zip_code
from fixed_postal_codes as A
where A.zip_code = ways_tags.value
and ways_tags.key = 'postcode')
where exists
(select *
from fixed_postal_codes as A
where A.zip_code = ways_tags.value
and ways_tags.key = 'postcode');
'''
c.execute(query)

query = '''
update nodes_tags
set value =
(select A.new_zip_code
from fixed_postal_codes as A
where A.zip_code = nodes_tags.value
and nodes_tags.key = 'postcode')
where exists
(select *
from fixed_postal_codes as A
where A.zip_code =  nodes_tags.value
and nodes_tags.key = 'postcode');
'''
c.execute(query)


# In[36]:

# Determine minimum and maximum latitude and longitude of the area described.
query = '''
select min(lat), max(lat)
from nodes;
'''
c.execute(query)
rows = c.fetchall()
print "Latitude"
pprint.pprint(rows)

query = '''
select min(lon), max(lon)
from nodes;
'''
c.execute(query)
rows = c.fetchall()
print "Longitude"
pprint.pprint(rows)


# In[ ]:

# Fix cities names
# 1. Create a table with cities names to fix in one column and fixed names in another

query = '''
create table fixed_cities
(city TEXT PRIMARY KEY NOT NULL,
new_city TEXT);
'''
c.execute(query)


# In[16]:

query = '''
insert into fixed_cities
values
('San José', 'San Jose'),
('sunnyvale', 'Sunnyvale'), 
('South Mary Avenue', 'Sunnyvale'),
('SUnnyvale', 'Sunnyvale'),
('cupertino', 'Cupertino');
'''
c.execute(query)


# In[37]:

query = '''
update ways_tags
set value = 
(select A.new_city
from fixed_cities as A
where A.city = ways_tags.value
and ways_tags.key = 'city')
where exists
(select *
from fixed_cities as A
where A.city = ways_tags.value
and ways_tags.key = 'city');
'''
c.execute(query)

query = '''
update nodes_tags
set value = 
(select A.new_city
from fixed_cities as A
where A.city = nodes_tags.value
and nodes_tags.key = 'city')
where exists
(select *
from fixed_cities as A
where A.city = nodes_tags.value
and nodes_tags.key = 'city');
'''
c.execute(query)


# In[38]:

# Correct cities names containing state abbreviation

query = '''
update ways_tags
set value = substr(value, 1, instr(value, 'CA') - 3)
where key = 'city'
and substr(value, instr(value, 'CA'), 2) = 'CA';
'''
c.execute(query)


# In[39]:

# Identify records with full address. Verify that address parts exist 
# as separate records with keys "street", "housenumber" etc. 
query = '''
select * from nodes_tags
where id in (select id from nodes_tags
where key = 'full');
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)



# In[40]:

# Insert missing records with address part.
query = '''
insert into nodes_tags
values(807626611, 'city', 'Sunnyvale', 'addr\r');
'''
c.execute(query)


# In[41]:

# Delete records with full address.
query = '''
delete from nodes_tags
where id in (select id from nodes_tags
where key = 'full')
and key = 'full';
'''
c.execute(query)


# In[ ]:



