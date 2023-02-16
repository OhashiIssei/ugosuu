class Update_From_Source(Category):
    def copy_from_myfile(self,myfile):
        self.name = myfile.name
        self.path = myfile.path
        return self
        
    def baseFile(self):
        MyFile.objects.filter(name = self.name).delete()
        return MyFile.objects.create(
            name = self.name,
            path = self.path
        )
    def baseCategory(self):
        Category.objects.filter(name = self.name).delete()
        return Category.objects.create(
            name = self.name,
            path = self.path
        )

    def Koukousuugaku(self):
        self.baseCategory().update_excelfiles()
    
    def Icons(self):
        self.baseFile().update_icons()

    def Myfile(self):
        self.baseCategory().update_my_folder()

    def Kakomon(self):
        self.baseCategory().update_kakomon_folder()

    def Note(self):
        self.baseCategory().update_note()
                
# Update_From_Source(
#     name = "高校数学",
#     path = "/Users/greenman/Desktop/web-projects/django_projects/ugosite/ugosite/math_data"
# ).Koukousuugaku()
        
# Update_From_Source(
#     name = "icons",
#     path = "/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/icons"
# ).Icons()
        
# Update_From_Source(
#     name = "講師関係",
#     path = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/講師関係'
# ).Myfile()

# Update_From_Source(
#     name = "大学別62年過去問題集",
#     path = '/Users/greenman/Library/Mobile Documents/com~apple~CloudDocs/旧帝大過去問',
#     description = "このモジュールには、旧帝7大+東工大の過去62年の問題が含まれています。",
#     type = "T",
# ).Kakomon()
            
# Update_From_Source(
#     name = "Notes",
#     path = '/Users/greenman/Desktop/web-projects/django_projects/ugosite/media_local/Notes'
# ).Note()

class Update_To_Source(Category):
    def baseCategory(self):
        Category.objects.filter(name = self.name).delete()
        return Category.objects.create(
            name = self.name,
            path = self.path
        )
    
    def baseFile(self):
        MyFile.objects.filter(name = self.name).delete()
        return MyFile.objects.create(
            name = self.name,
            path = self.path
        )

    def Koukousuugaku(self):
        self.baseCategory().update_excelfiles()
            
    
    def Icons(self):
        self.baseFile().update_icons()

    def Myfile(self):
        self.baseCategory().update_my_folder()

    def Kakomon(self):
        self.baseCategory().update_kakomon_folder()

    def Note(self):
        self.baseCategory().update_note()