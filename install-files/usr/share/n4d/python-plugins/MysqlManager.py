
import tempfile
import shutil
import os
import subprocess
import time

class MysqlManager:
	
	
	def __init__(self):
		
		pass
		
	#def init
	
	def get_time(self):
		
		return get_backup_name("MysqlManager")
		
	#def get_time
	
	
	def backup(self,dir="/backup/"):
		
		try:
		
			file_path=dir+"/"+self.get_time()
			tmp_dir=tempfile.mkdtemp()
			
			ret=os.system("mysql_root_passwd -g")
			
			if ret!=0:
				os.system("mysql_root_passwd -i")
			
			cmd="mysqldump -u root -p$(mysql_root_passwd -g) --routines --all-databases --flush-privileges > %s/backup.sql"%(tmp_dir)
			os.system(cmd)
			
			if os.path.exists(tmp_dir+"/backup.sql"):
				tar=tarfile.open(file_path,"w:gz")
				tar.add(tmp_dir+"/backup.sql",arcname="backup.sql")
				if os.path.exists("/root/.my.cnf"):
					tar.add("/root/.my.cnf",arcname="my.cnf")
				tar.close()
				
				os.system("chmod 600 %s"%file_path)
				
				return [True,file_path]
			
		except Exception as e:
			return [False,str(e)]
			
		return [False,"Mysqldump failed"]
		
	#def test
	
	def restore(self,file_path=None):

		if file_path==None:
			for f in sorted(os.listdir("/backup"),reverse=True):
				if "MysqlManager" in f:
					file_path="/backup/"+f
					break

		if file_path==None:
			return [False,"No backup file found"]
			
		try:

			if os.path.exists(file_path):
				
				tmp_dir=tempfile.mkdtemp()
				tar=tarfile.open(file_path,"r")
				tar.extractall(tmp_dir)
				tar.close()
				#os.system("chmod 600 %s"%file_path)
				
				if os.path.exists(tmp_dir+"/my.cnf"):
					shutil.copy(tmp_dir+"/my.cnf","/root/.my.cnf")
					os.system("chmod 600 /root/.my.cnf")
					os.system("mysql_root_passwd -i")
					
				if os.path.exists(tmp_dir+"/backup.sql"):
					cmd="mysql -u root -p$(mysql_root_passwd -g) < %s"%(tmp_dir+"/backup.sql")
					os.system(cmd)
					
				#Upgrade db if backup is from version <=5.5 (Trusty)
				version=objects["ServerBackupManager"].restoring_version
				majorBackupVersion=int(version[0:version.find('.')])
				if majorBackupVersion<=15:
					print "Upgrading from an ancient version..."
					cmd="mysql_upgrade -p$(mysql_root_passwd -g)"
					os.system(cmd)

				#Fix pwd for moodle and pmb
				apps=['lliurex-moodle','lliurex-pmb']
				for app in apps:
					cmd='lliurex-sgbd --upgrade '+app
					os.system(cmd)
				
				#Fix for pmb imports
				self.change_pmb_version()

				return [True,""]
				
		except Exception as e:
			print e
			return [False,file_path + ": " + str(e)]
		
	#def test

	def change_pmb_version(self):

		mysql_command='mysql -uroot -p$(sudo mysql_root_passwd -g) -e '
		#Get bdd_version value from parametres table
		sql='"select valeur_param from pmb.parametres where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
		cmd=mysql_command + sql
		p=subprocess.check_output(cmd,shell=True)
		version=p.split("\n")[1]
		
		if version=="v4.47":
			sql='"update pmb.parametres set valeur_param=\'vLlxNemo\' where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
			cmd=mysql_command + sql
			os.system(cmd)
		elif 	version=="v5.10":
			sql='"update pmb.parametres set valeur_param=\'vLlxPandora\' where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
			cmd=mysql_command + sql
			os.system(cmd)
	
		elif version=="v5.14":
			sql='"update pmb.parametres set valeur_param=\'vLlxTrusty\' where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
			cmd=mysql_command + sql
			os.system(cmd)

	#def change_pmb_version
	
#class CupsManager

if __name__=="__main__":
	
	m=MysqlManager()
		
	m.backup()

	

