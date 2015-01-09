# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from django.db import connection

class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class SocioclipBookmarkTags(models.Model):
    id = models.BigIntegerField(primary_key=True)
    bookmark = models.ForeignKey('SocioclipBookmarks')
    tag = models.ForeignKey('SocioclipTags')
    tag_date = models.DateField(auto_now_add = True)

    def __unicode__(self):
        return u'%s %s' % (self.bookmark,self.tag)    

    class Meta:
        managed = False
        db_table = 'socioclip_bookmark_tags'
        unique_together = (('bookmark', 'tag'),)


class SocioclipBookmarks(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    person = models.ForeignKey('SocioclipUsers')
    source = models.TextField()
    type = models.CharField(max_length=10)
    permalink = models.TextField()
    postby = models.CharField(blank=True, null=True, max_length=60)
    archived = models.IntegerField(default=0)
    thumbnail = models.TextField(blank=True, null=True)
    title = models.CharField(db_column='Title', max_length=350, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)
    category_id = models.IntegerField(default=1)
    folder = models.ForeignKey('SocioclipFolders', blank=True, null=True)
    tag_list = models.ForeignKey('SocioclipTagLists', blank=True, null=True)
    bookmark_date = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return u'%s %s' % (self.bookmark_id,self.person)     

    class Meta:
        managed = False
        db_table = 'socioclip_bookmarks'


class SocioclipFolders(models.Model):
    folder_id = models.BigIntegerField(primary_key=True)
    parent_folder = models.ForeignKey('self', blank=True, null=True)
    folder_name = models.CharField(max_length=200, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add = True)
    created_by = models.BigIntegerField(blank=True, null=True)

    def __unicode__(self):
        return u'%s %s' % (self.folder_id,self.folder_name)         

    class Meta:
        managed = False
        db_table = 'socioclip_folders'


class SocioclipTagLists(models.Model):
    tag_list_id = models.BigIntegerField(primary_key=True)
    tag_list_name = models.CharField(max_length=200)
    tag = models.ForeignKey('SocioclipTags')
    created_by = models.BigIntegerField()
    creation_date = models.DateTimeField()

    def __unicode__(self):
        return u'%s %s' % (self.tag_list_id,self.tag_list_name)          

    class Meta:
        managed = False
        db_table = 'socioclip_tag_lists'


class SocioclipTags(models.Model):
    tag_id = models.BigIntegerField(primary_key=True)
    tag_text = models.CharField(unique=True, max_length=200)
    category = models.CharField(max_length=2,default='DF')

    def __unicode__(self):
        return u'%s %s' % (self.tag_id,self.tag_text)        

    class Meta:
        managed = False
        db_table = 'socioclip_tags'


class SocioclipUsers(models.Model):
    person_id = models.BigIntegerField(primary_key=True)
    datestamp = models.DateField(db_column='DATESTAMP', blank=True, null=True)  # Field name made lowercase.
    time = models.CharField(db_column='TIME', max_length=8, blank=True, null=True)  # Field name made lowercase.
    ip = models.CharField(db_column='IP', max_length=15, blank=True, null=True)  # Field name made lowercase.
    browser = models.TextField(db_column='BROWSER', blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(unique=True, max_length=40)
    password = models.CharField(db_column='PASSWORD', max_length=255, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    clips_left = models.IntegerField(default=30)
    type = models.CharField(db_column='Type', max_length=1,default='P')  # Field name made lowercase.

    def __unicode__(self):
        return u'%s %s' % (self.person_id,self.email)      

    class Meta:
        managed = False
        db_table = 'socioclip_users'


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def fetch_home_page_data(emailid,archive_flag, folder_id):
    cursor = connection.cursor()

    cursor.execute("select sbtt.*,st.* from \
    socioclip_users su, \
    (select sb.*,sbt.tag_id as b_tag_id \
    from socioclip_bookmarks sb left join socioclip_bookmark_tags sbt on sb.bookmark_id = sbt.bookmark_id) sbtt \
    left join socioclip_tags st on sbtt.b_tag_id = st.tag_id \
    where su.email = %s \
    and su.person_id = sbtt.person_id  \
    and sbtt.archived = %s \
    and ifnull(sbtt.folder_id, -1) = ifnull(%s,-1) \
    order by bookmark_date desc, sbtt.bookmark_id", [emailid,archive_flag,folder_id])

    rows = dictfetchall(cursor)

    proper_rows = []
    temp_bookmark_tag = {}
    temp_bookmark_id = -1
    count = 1

    for row in rows:      
        if temp_bookmark_id != row['bookmark_id']:
            if temp_bookmark_tag:
                proper_rows.append(temp_bookmark_tag)
            temp_bookmark_tag = {}
            l_postby = row['postby']
            l_postby = (l_postby[:18] + '..') if len(l_postby) > 20 else l_postby
            temp_bookmark = {'bookmark_id':row['bookmark_id'], 'source' : row['source'], 'type' : row['type'], 
            'permalink':row['permalink'], 'postby':l_postby, 'thumbnail':row['thumbnail'], 
            'description':row['description'], 'bookmark_date':row['bookmark_date'], 'bookmark_title':row['Title']}
            temp_bookmark_id = row['bookmark_id']
            temp_tag = {'tag_id':row['tag_id'], 'tag_text':row['tag_text'], 'category':row['category']}
            temp_tag_list = [temp_tag]
            temp_bookmark_tag = {'bookmark':temp_bookmark,'tag':temp_tag_list}
        else:
            temp_tag = {'tag_id':row['tag_id'], 'tag_text':row['tag_text'], 'category':row['category']}
            temp_bookmark_tag['tag'].append(temp_tag)
    if temp_bookmark_id != -1:
        proper_rows.append(temp_bookmark_tag)
    cursor.close()

    return proper_rows           
