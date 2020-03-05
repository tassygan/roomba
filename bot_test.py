from users import Seeker

globalvars = {'chat_id':None, 'mode':None}
seeker = Seeker()
seeker.name = 'Aidar'
globalvars['chat_id'] = seeker
print(globalvars)