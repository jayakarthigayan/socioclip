from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.context_processors import csrf
from socioclip.models import SocioclipUsers, SocioclipBookmarks, fetch_home_page_data, SocioclipFolders, SocioclipTags, SocioclipBookmarkTags
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.template import Context
from django.middleware.csrf import get_token
from urlparse import urlparse
import bcrypt
import hashlib

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Create your views here.

# View function to load the initial index page
def index(request):
	session_exists = request.session.get('scan_me','error')	
	if session_exists != 'error':
		return redirect('/home/')
	return render(request, 'login.html')

def createcookie(request):
	csrf_token = get_token(request)
	print csrf_token
	return HttpResponse('created')

# View function to handle the login process
def login(request):
	if request.method == 'POST':
		emailid = request.POST.get('emailid')
		password = request.POST.get('password')
		comp_resul = True
		name = ''	
		try:
			user = SocioclipUsers.objects.select_related().get(email = emailid)
			name = user.name
			password_hash = bcrypt.hashpw(password, user.password.encode())
			ser_pass_hash_bytes = user.password.encode()
			count = 1
			for i in password_hash:			
				if count <= len(ser_pass_hash_bytes):
					comp_resul &= (i == ser_pass_hash_bytes[count -1])
					count += 1
				else:
					comp_resul &= False
		except ObjectDoesNotExist:
			for i in range(0,60):			
				comp_resul &= False
			return render(request, 'login.html', {'result_val':'Login Failed'})
		
		if comp_resul:		
			request.session['scan_me'] = emailid
			return redirect('/home/')					
		else:
			return render(request, 'login.html', {'result_val':'Login Failed'})		
	return render(request, 'login.html', {'result_val':'Login Failed'})


# View function to load the home page after successful login
def home(request):
	emailid = request.session.get('scan_me','error')
	name = ''	
	print request.method
	if emailid != 'error':
		try:
			user = SocioclipUsers.objects.select_related().get(email = emailid)
			name = user.name
			rows = fetch_home_page_data(emailid,0,None)
			folder_list = SocioclipFolders.objects.filter(created_by = user.person_id, parent_folder_id = None, folder_name = 'pinned')
			if user.type == 'P':
				return render(request, 'home_user.html', {'result_val':'Welcome '+name,'bookmark_data':rows, 'clip_count':user.clips_left, 'page_mode':'home', 'top_folder_list':folder_list})
		except ObjectDoesNotExist:
			return render(request, 'login.html', {'result_val':'Serious error happened.Sorry!'})
	else:
		return render(request, 'login.html', {'result_val':'You are not authorized to view this page. Please login to continue'})
	return render(request, 'login.html', {'result_val':'Some unhandled exception occurred. Sorry!'})

# View function to handle the logout functionality
def logout(request):
	request.session.flush()
	return render(request, 'login.html')

# View function to handle the archive functionality
def archive(request):
	emailid = request.session.get('scan_me','error')
	if emailid != 'error' and request.method == 'POST':
		p_bookmark_id = request.POST.get('bookmark_id')
		try:
			archive_bookmark = SocioclipBookmarks.objects.get(bookmark_id = int(p_bookmark_id))
			archive_bookmark.archived = 1
			archive_bookmark.save()
		except ObjectDoesNotExist:
			return HttpResponse('-1')	
	return HttpResponse('1')	

# View function to get the clip left count
def clipcount(request):
	emailid = request.session.get('scan_me','error')
	if emailid != 'error':
		user = SocioclipUsers.objects.select_related().get(email = emailid)
		if user.type == 'P':
			return HttpResponse(user.clips_left)
	return HttpResponse('0')

# View function to view the list of archived bookmarks
def viewarchive(request):
	emailid = request.session.get('scan_me','error')
	name = ''	
	if emailid != 'error':
		try:
			user = SocioclipUsers.objects.select_related().get(email = emailid)
			name = user.name
			rows = fetch_home_page_data(emailid,1,None)
			folder_list = SocioclipFolders.objects.filter(created_by = user.person_id, parent_folder_id = None).exclude(folder_name = 'pinned').order_by("folder_name")
			if user.type == 'P':
				return render(request, 'home_user.html', {'result_val':'Welcome '+name,'bookmark_data':rows, 'clip_count':user.clips_left, 'page_mode':'archive', 'top_folder_list':folder_list})
		except ObjectDoesNotExist:
			return render(request, 'login.html', {'result_val':'Serious error happened.Sorry!'})
	return render(request, 'login.html', {'result_val':'Some unhandled exception occurred. Sorry!'})

# View function to create a folder in the archive page
def createfolder(request):
	emailid = request.session.get('scan_me','error')	
	if emailid != 'error' and request.method == 'POST':
		p_new_folder_name = request.POST.get('new_folder_name')
		p_parent_folder_id = request.POST.get('parent_folder_id')		
		if not p_parent_folder_id:
			p_parent_folder_id = None
		else:
		 	p_parent_folder_id = int(p_parent_folder_id)
		try:
			user = SocioclipUsers.objects.get(email = emailid)
			folder_already_exists = SocioclipFolders.objects.filter(folder_name = p_new_folder_name, parent_folder = p_parent_folder_id, created_by = user.person_id).exists()
			if folder_already_exists:
				return HttpResponse('Folder creation failed. Folder name already exists')
			else:
				parent_folder_id_exists = True
				if p_parent_folder_id is not None:
					parent_folder_id_exists = SocioclipFolders.objects.filter(folder_id = p_parent_folder_id, created_by = user.person_id).exists()			
				if parent_folder_id_exists:					
					try:
						if p_parent_folder_id is not None:
							p_parent_folder_id = SocioclipFolders.objects.get(folder_id = p_parent_folder_id, created_by = user.person_id)
						new_folder = SocioclipFolders(folder_name = p_new_folder_name, parent_folder = p_parent_folder_id, created_by = user.person_id)
						new_folder.save()
					except Exception,e:
						print str(e)						
				else:
					return HttpResponse('Folder creation failed. Parent Folder id doesn''t exists')						
		except ObjectDoesNotExist:
			return redirect('/archive/',{'result_val':'Error ', 'page_mode':'archive'})
	return HttpResponse('Folder "'+ p_new_folder_name +'" created successfully')

# View function to display the bookmarks within a folder.
def viewfoldercont(request,url,folder_id):
	emailid = request.session.get('scan_me','error')		
	if emailid != 'error':
		try:
			p_folder_id = int(folder_id)			
			user = SocioclipUsers.objects.select_related().get(email = emailid)
			name = user.name
			row = []
			if url == 'home':
				rows = fetch_home_page_data(emailid,0,p_folder_id)
				folder_list = SocioclipFolders.objects.filter(created_by = user.person_id, parent_folder_id = None, folder_name = 'pinned')
			else:
				rows = fetch_home_page_data(emailid,1,p_folder_id)
				folder_list = SocioclipFolders.objects.filter(created_by = user.person_id, parent_folder_id = None).order_by("folder_name")			
			if user.type == 'P':
				page_mode = 'archive'
				if url == 'home':
					page_mode = 'home'
				return render(request, 'home_user.html', {'result_val':'Welcome '+name,'bookmark_data':rows, 'page_mode':page_mode, 'top_folder_list':folder_list})			
		except ValueError:
			return render(request, 'login.html', {'result_val':'Serious error happened.Sorry!'})			
		except ObjectDoesNotExist:
			return render(request, 'login.html', {'result_val':'Serious error happened.Sorry!'})			
	return render(request, 'login.html', {'result_val':'Some unhandled exception occurred. Sorry!'})

# View function to move a bookmark to a folder.
def movebookmark(request):
	emailid = request.session.get('scan_me','error')	
	if emailid != 'error' and request.method == 'POST':
		p_bookmark_id = request.POST.get('bookmark_id')
		p_folder_id = request.POST.get('folder_id')
		if p_folder_id:			
			try:
				p_folder_id = int(p_folder_id)
				user = SocioclipUsers.objects.get(email = emailid)			
				folder_id_exists = False
				if p_folder_id is not None:
					folder_id_exists = SocioclipFolders.objects.filter(folder_id = p_folder_id, created_by = user.person_id).exists()			
				if p_bookmark_id is not None:
					bookmark_id_exists = SocioclipBookmarks.objects.filter(bookmark_id = p_bookmark_id).exists()
				if folder_id_exists and bookmark_id_exists:					
					bookmark_move = SocioclipBookmarks.objects.select_related().get(bookmark_id = p_bookmark_id)
					assign_folder = SocioclipFolders.objects.get(folder_id = p_folder_id)
					bookmark_move.folder = assign_folder
					bookmark_move.save()
					return HttpResponse('Bookmark "'+ p_bookmark_id +'" moved successfully')
				else:
					return HttpResponse('Move Bookmark failed. Folder id doesn''t exists')						
			except ObjectDoesNotExist:
				return redirect('/archive/',{'result_val':'Error ', 'page_mode':'archive'})
	return HttpResponse('Move Bookmark failed. Due to some unknown error')

# View function to check whether the email id already exists
def check_user_email(request):
	if request.method == 'POST':
		emailid = request.POST.get('emailid')
		user_exists = SocioclipUsers.objects.filter(email = emailid).exists()
		if user_exists:
			return HttpResponse('User/Email id '+ emailid +' already exists')
		else:
			return HttpResponse('User/Email id is available')
	else:
		return HttpResponse('Fatal Error while checking user')

# View function to handle new user signup.
def signup(request):
	if request.method == 'POST':
		p_emailid = request.POST.get('s_emailid')
		p_user_name = request.POST.get('s_name')
		p_password = request.POST.get('s_password')
		user_exists = SocioclipUsers.objects.filter(email = p_emailid).exists()
		if user_exists:
			return render(request, 'login.html', {'result_val':'User Name/Email id already exists'})
		else:
			password_hash = bcrypt.hashpw(p_password, bcrypt.gensalt())
			user = SocioclipUsers(email = p_emailid, name = p_user_name, password = password_hash)
			user.save()
			user = SocioclipUsers.objects.select_related().get(email = p_emailid)
			pinned_folder = SocioclipFolders(parent_folder_id = None, folder_name = 'pinned', created_by = user.person_id)
			pinned_folder.save()
			send_mail(p_emailid)
			return render(request, 'login.html', {'result_val':'User successfully created'})
	else:
		return render(request, 'login.html', {'result_val':'Fatal Error while Sign Up'})

# View function to send confirmation mail to the new user.
def send_mail(p_emailid):
	# Open a plain text file for reading.  For this example, assume that
	# the text file contains only ASCII characters.
	# Create a text/plain message
	msg = MIMEText('This is a test mail. Welcome to socioclip')

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = 'Welcome to Socioclip'
	msg['From'] = 'socioclip@socioclip.com'
	msg['To'] = p_emailid

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	server = smtplib.SMTP('smtpcorp.com:2525')
	server.ehlo()
	server.starttls()
	server.login('jayakarthigayan@outlook.com','1357qetu')
	server.sendmail('socioclip@socioclip.com', p_emailid, msg.as_string())
	server.quit()

def getsubfolderlist(request):
	emailid = request.session.get('scan_me','error')	
	if emailid != 'error' and request.method == 'POST':
		p_folder_id = request.POST.get('p_folder_id')
		p_folder_id = p_folder_id.split("_",1)[0]
		if p_folder_id:
			try:
				user = SocioclipUsers.objects.get(email = emailid)
				subfolders_list = SocioclipFolders.objects.filter(parent_folder = p_folder_id, created_by = user.person_id).order_by('folder_name')
				t = get_template('subfolder.html')
				html = t.render(Context({'folder_lists':subfolders_list}))
				return render(request, 'subfolder.html', {'folder_lists':subfolders_list})
			except ObjectDoesNotExist:
				return HttpResponse('User not found exception')

def createbookmark(request):
	try:
		if request.method == 'POST':
			p_emailid = request.POST.get('p_id')
			p_title = request.POST.get('p_title')
			p_thumbnail = request.POST.get('p_thumbnail')
			p_desc = request.POST.get('p_desc')
			p_perm_link = request.POST.get('p_perm_link')
			p_tags = request.POST.get('p_tags')
			p_post_by = request.POST.get('p_postby')
			print "p_emailid", p_emailid
			print "p_title", p_title
			print "p_thumbnail", p_thumbnail
			print "p_desc", p_desc
			print "p_perm_link", p_perm_link
			print "p_post_by", p_post_by
			print "p_tags", p_tags
			if p_tags:
				for tag in p_tags.split(","):
					print tag
			if p_emailid:
				try:
					user = SocioclipUsers.objects.select_related().get(email = p_emailid)
					bookmark = SocioclipBookmarks()
					bookmark.person = user
					if p_perm_link:
						bookmark.permalink = p_perm_link
					else:
						return HttpResponse('Link cannot be empty')		
					if p_thumbnail or p_title:
						if p_thumbnail:
							bookmark.thumbnail = p_thumbnail
							bookmark.type = 'Photo'
						if p_title:
							bookmark.title = p_title
							bookmark.type = 'Text'
					else:
						return HttpResponse('Both Thumbnail and Title cannot be empty')			
					if p_post_by:
						bookmark.postby = p_post_by
					if p_desc:
						bookmark.description = p_desc		
					parsed_uri = urlparse( p_perm_link )
					source = '{uri.netloc}'.format(uri=parsed_uri)
					if source:
						bookmark.source = source
					bookmark.folder = None
					bookmark.tag_list = None
					bookmark.save()
					if p_tags:
						for tag in p_tags.split(","):
							tag = tag.upper()
							try:
								tag_obj = SocioclipTags.objects.get(tag_text = tag)
								bookmark_tag = SocioclipBookmarkTags(bookmark = bookmark, tag = tag_obj)
								bookmark_tag.save()
							except ObjectDoesNotExist:
								tag_obj = SocioclipTags(tag_text = tag)
								tag_obj.save()
								tag_obj = SocioclipTags.objects.get(tag_text = tag)
								bookmark_tag = SocioclipBookmarkTags(bookmark = bookmark, tag = tag_obj)
								bookmark_tag.save()
					return HttpResponse('Bookmark created successfully')
				except ObjectDoesNotExist:
					return HttpResponse('Invalid User Error')		
			else:
				return HttpResponse('Email id not valid')			
			return HttpResponse('Fatal Error while creating bookmark')
		else:
			return HttpResponse('Not an authorized request')
	except Exception,e:
		print str(e)