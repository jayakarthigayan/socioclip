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


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class SocioclipBookmarkTags(models.Model):
    bookmark = models.ForeignKey('SocioclipBookmarks')
    tag = models.ForeignKey('SocioclipTags')
    tag_date = models.DateField()

    def __unicode__(self):
        return u'%s %s' % (self.bookmark,self.tag)

    class Meta:
        managed = False
        db_table = 'socioclip_bookmark_tags'
        unique_together = (('bookmark_id', 'tag_id'),)


class SocioclipBookmarks(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    person_id = models.BigIntegerField()
    source = models.TextField()
    type = models.CharField(max_length=10)
    permalink = models.TextField()
    postby = models.CharField(max_length=60)
    archived = models.IntegerField()
    thumbnail = models.TextField()
    description = models.TextField()
    category_id = models.IntegerField()
    folder = models.ForeignKey('SocioclipFolders', blank=True, null=True)
    tag_list = models.ForeignKey('SocioclipTagLists', blank=True, null=True)

    def __unicode__(self):
        return u'%s %s' % (self.bookmark_id,self.person_id)

    class Meta:
        managed = False
        db_table = 'socioclip_bookmarks'


class SocioclipFolders(models.Model):
    folder_id = models.BigIntegerField(primary_key=True)
    parent_folder = models.ForeignKey('self', blank=True, null=True)
    folder_name = models.CharField(max_length=200, blank=True, null=True)
    creation_date = models.DateTimeField(blank=True, null=True)
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
    category = models.CharField(max_length=2)

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
    clips_left = models.IntegerField()
    type = models.CharField(db_column='Type', max_length=1)  # Field name made lowercase.

    def __unicode__(self):
        return u'%s %s' % (self.person_id,self.email)        

    class Meta:
        managed = False
        db_table = 'socioclip_users'
