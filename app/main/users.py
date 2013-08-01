import ldap
import ldap.filter

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from app.main.models import *
from app.main.random_str import *

def gen_forgot_password(user):
	"""
	Generate a password reset key for the user and store it in Memcached.
	Returns the generated key.
	"""
	key = GenRandomHash(settings.SECRET_KEY + str(timezone.now()))
	cache.set(key, user.id, settings.PASSWORD_RESET_EXPIRY)
	return key

def lookup_user(data):
	"""
	Return list of matching user objects based on cnetid or first and last name.
	If no local cnetid match is found, LDAP search is initiated.
	A User object is created for each new LDAP record.
	"""
	matches = []
	cnetid_already_found = set() # prevent duplicates from being added during LDAP search
	if data.get('cnetid'):
		data['cnetid'] = ldap.filter.escape_filter_chars(data['cnetid'].encode('utf-8'))
		try:
			return [User.objects.get(profile__cnetid=data['cnetid'])]
		except User.DoesNotExist:
			pass
	elif data.get('first_name') and data.get('last_name'):
		data['first_name'] = ldap.filter.escape_filter_chars(data['first_name'].encode('utf-8').title())
		data['last_name'] = ldap.filter.escape_filter_chars(data['last_name'].encode('utf-8').title())
		#local_matches = User.objects.filter(first_name=data['first_name'], last_name=data['last_name'])
		local_matches = User.objects.filter(last_name=data['last_name']) # Using just last name here is OK because local queries are relatively cheap
		for user in local_matches:
			cnetid_already_found.add(user.profile.cnetid)
		matches.extend(list(local_matches))
	else:
		raise Exception("CNetID or first_name and last_name must be provided")
		
	exact_match = None
	l = ldap.initialize(settings.LDAP_SERVER)
	l.start_tls_s()
	if data['cnetid']:
		lq = "(&(uid=%s)(objectclass=inetOrgPerson))" % (data['cnetid'])
	else:
		# find users whose cn contains their first name and ends with last name
		lq = "(&(cn=*%s*)(sn=%s)(objectclass=inetOrgPerson))" % (data['first_name'], data['last_name'])
	msgid = l.search_ext(settings.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, lq, ['uid', 'givenName', 'sn', 'cn', 'ucMiddleName', 'displayName', 'chicagoID', 'mail', 'ucisMemberOf']) 
	results = []
	while True:
		try:
			result_type, result_data = l.result(msgid, 0)
		except:
			break
		if result_data:
			results.append(result_data[0])
		else:
			break
	for dn, entry in results:
		# first filter for eligibility
		if not 'uc:applications:shibboleth:incommon' in entry.get('ucisMemberOf', {}):
			continue
		# Get or create User objects
		user = None
		try:
			# this should never return a match, but we check just in case we somehow missed it
			user = User.objects.get(username=entry['chicagoID'][0])
		except User.DoesNotExist:
			first_name, last_name = "", ""
			if entry.get('sn') and entry.get('uid'):
				last_name = entry['sn'][0]
				if entry.get('givenName'):
					# use first name as-is
					first_name = entry['givenName'][0]
				elif entry.get('displayName'):
					# strip last name from displayName
					displayName = entry['displayName'][0]
					lastIndex = displayName.rfind(last_name)
					if lastIndex:
						first_name = displayName[:lastIndex].strip()
					else:
						first_name = displayName
				elif entry.get('cn'):
					# strip last and middle name from cn
					cn = entry['cn'][0]
					lastIndex = cn.rfind(last_name)
					if lastIndex:
						first_name = cn[:lastIndex].strip()
					else:
						first_name = cn
					if entry.get('ucMiddleName'):
						middle = entry['ucMiddleName'][0]
						midIndex = first_name.rfind(middle)
						if midIndex:
							first_name = first_name[:midIndex].strip()
					
				user = User.objects.create_user(username=entry['chicagoID'][0], email="%s@uchicago.edu" % (entry['uid'][0]), first_name=first_name, last_name=last_name)
				user.set_unusable_password()
				user.save()
				user.profile.cnetid = entry['uid'][0]
				user.profile.save()

		if user:
			if data['cnetid'] and entry['uid'][0] == data['cnetid']:
				exact_match = user
			elif (data['first_name'] and data['last_name']) and (user.first_name == data['first_name'] and user.last_name == data['last_name']):
				if entry['uid'][0] not in cnetid_already_found:	
					matches.append(user)
	if exact_match:
		return [exact_match]
	return matches or []
	
