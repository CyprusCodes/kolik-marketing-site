"""Deterministic text-only localisation of supplied Kolik product captures.
Requires Pillow, fonttools and brotli. Source captures stay outside the web tree.
Usage: python scripts/prepare_product_media.py --sources PATH --output PATH
"""
import argparse, json, re, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args();ROOT=Path(__file__).resolve().parents[1];SRC=args.sources;OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
FONTDIR=Path(tempfile.gettempdir())/'kolik-fixed-fonts';FONTDIR.mkdir(exist_ok=True)
fonts={};cmaps={};manifest={}
for family in ['inter','dm-sans']:
 for subset in ['latin','latin-ext']:
  source=ROOT/f'assets/fonts/{family}-{subset}.woff2'
  for weight in [400,600,700]:
   font=TTFont(source);font.flavor=None
   if 'fvar' in font:font=instantiateVariableFont(font,{'wght':weight},inplace=True)
   target=FONTDIR/f'{family}-{subset}-{weight}.ttf';font.save(target)
   fonts[family,subset,weight]=target;cmaps[family,subset,weight]=font.getBestCmap()
INK='#101828';MUTED='#6b7280';PURPLE='#9b75ed';NAVY='#1c2536';WHITE='#ffffff';cache={}
def font_for(char,size,weight=400,family='inter'):
 subset='latin' if ord(char) in cmaps[family,'latin',weight] else 'latin-ext'
 key=family,subset,weight,size
 if key not in cache:cache[key]=ImageFont.truetype(str(fonts[family,subset,weight]),size)
 return cache[key]
def measure(text,size,weight=400,family='inter'):
 return sum(font_for(c,size,weight,family).getlength(c) for c in text)
def line(draw,xy,text,size=18,weight=400,fill=INK,family='inter'):
 x,y=xy
 for c in text:
  f=font_for(c,size,weight,family);draw.text((x,y),c,font=f,fill=fill,anchor='lm');x+=f.getlength(c)
class Capture:
 def __init__(self,name):self.im=Image.open(SRC/name).convert('RGB');self.draw=ImageDraw.Draw(self.im);self.source=name;self.boxes=[]
 def patch(self,x,y,w,h,text,size=18,weight=400,color=INK,bg=WHITE,align='left'):
  self.draw.rectangle((x,y,x+w-1,y+h-1),fill=bg);self.boxes.append([x,y,w,h])
  if not text:return
  lines=text.split('\n');size=int(size)
  while max(measure(s,size,weight) for s in lines)>w-4 and size>12:size-=1
  step=size*1.35;cy=y+h/2-(len(lines)-1)*step/2
  for s in lines:
   tw=measure(s,size,weight);px=x+2 if align=='left' else (x+w-tw-2 if align=='right' else x+(w-tw)/2)
   line(self.draw,(px,cy),s,size,weight,color);cy+=step
 def save(self,name,lang,crop=None):
  im=self.im.crop(crop) if crop else self.im;im.save(OUT/name,optimize=True)
  manifest[name]={'language':lang,'font':'Inter','source':self.source,'size':list(im.size),'text_edit_regions':self.boxes}
  return im

def sidebar(c,en,active=None):
 c.patch(68,82,203,31,'Kolik Demo',18,600,WHITE,NAVY)
 if en:
  c.patch(68,113,203,27,'Company Admin',16,400,'#a5afc0',NAVY)
  for y,label in zip([166,208,251,294,336,379,422],['Dashboard','Employees','Leaves','Calendar','Meeting Rooms','Support Tickets','AI Assistant']):
   bg='#252f40' if label==active else NAVY
   c.patch(53,y,250,30,label,18,600,'#ffffff' if label==active else '#a5afc0',bg)
  # Bottom button follows the image height.
  if c.source.startswith(('profile-','dashboard-')) or c.source=='meeting-rooms.png':
   y=c.im.height-51
   c.patch(108,y,180,28,'Admin Panel',18,600,WHITE,c.im.getpixel((280,y)))

def profile(en):
 lang='en' if en else 'tr';c=Capture('profile-'+lang+'.png');name='Alex Morgan' if en else 'Deniz Aksoy';manager='Emma Wilson' if en else 'Ayşe Demir'
 sidebar(c,en);c.patch(651,24,230,30,name,18,600);c.patch(400,120,600,63,name,44,700)
 c.patch(812,245,430,42,name,30,700);c.patch(812,291,500,30,'Software Engineer' if en else 'Yazılım Mühendisi',20,color=MUTED)
 c.patch(812,331,500,28,'Engineering' if en else 'Yazılım Geliştirme',18,color=MUTED)
 c.patch(812,360,700,27,('Manager: ' if en else 'Yönetici: ')+manager,18,color=MUTED)
 c.patch(700,295,68,40,'AM' if en else 'DA',36,600,'#080808','#9c76ed',align='center')
 c.patch(1837,25,35,30,'AM' if en else 'DA',16,600,'#101828','#f5f6f8',align='center')
 c.patch(685,507,410,32,'3 Nov 2025' if en else '03.11.2025',20)
 c.patch(685,608,410,32,'1 year 17 days' if en else '1 yıl 17 gün',20)
 c.patch(1277,608,530,32,'Permanent' if en else 'Belirsiz süreli',20)
 c.patch(685,776,410,32,'Kolik Demo',20)
 c.patch(1277,776,530,32,'Engineering' if en else 'Yazılım Geliştirme',20)
 c.patch(685,842,400,29,'Team' if en else 'Ekip',18,color=MUTED)
 c.patch(685,876,410,32,'Platform Team' if en else 'Platform Ekibi',20)
 c.patch(1277,842,530,29,'Work Location' if en else 'Görev Yeri',18,color=MUTED)
 c.patch(1277,876,530,32,'Nicosia Head Office' if en else 'Lefkoşa Merkez Ofis',20)
 c.patch(685,978,500,32,'Software Engineer' if en else 'Yazılım Mühendisi',20)
 c.patch(1277,978,530,32,manager,20)
 c.save('employee-profile-'+lang+'.png',lang,(0,0,1900,1017))

def dashboard(en):
 lang='en' if en else 'tr';c=Capture('dashboard-'+lang+'.png');sidebar(c,en,'Dashboard')
 c.patch(350,160,1200,58,'Welcome, Alex Morgan' if en else 'Hoş geldiniz, Deniz Aksoy',42,700)
 c.patch(1837,25,35,30,'AM' if en else 'DA',16,600,INK,'#f5f6f8',align='center')
 c.patch(550,350,258,30,'6 days used / 20 days total' if en else '6 gün kullanıldı / 20 gün toplam',16,color=MUTED,align='right')
 c.patch(407,408,385,30,'1 leave request awaiting approval' if en else '1 izin talebiniz onay bekliyor',18,color=MUTED)
 c.draw.rounded_rectangle((376,322,804,331),radius=5,fill='#e9e0f8');c.draw.rounded_rectangle((376,322,676,331),radius=5,fill='#a27bee')
 c.patch(375,617,400,30,'3 broadcasts sent this month' if en else 'Bu ay 3 duyuru gönderildi',18,color=MUTED)
 c.patch(375,696,400,32,'December team meeting' if en else 'Aralık ekip toplantısı',18)
 c.patch(905,643,49,27,'JAN' if en else 'OCA',14,color=MUTED,bg='#f5f6f8',align='center');c.patch(905,670,49,28,'1',24,bg='#f5f6f8',align='center')
 c.patch(965,638,355,30,'New Year’s Day' if en else 'Yılbaşı',18);c.patch(965,669,355,31,'1 Jan 2027 · In 42 days' if en else '1 Ocak 2027 · 42 gün içinde',16,color=MUTED)
 people=[('OT','Olivia Taylor','Human Resources','23 Nov','3 days'),('JP','James Parker','Operations','26 Nov','6 days'),('EW','Emma Wilson','Engineering','29 Nov','9 days'),('DC','Daniel Clark','Finance','2 Dec','12 days')] if en else [('SY','Selin Yurt','İnsan Kaynakları','23 Kas','3 gün'),('MK','Murat Kaya','Operasyon','26 Kas','6 gün'),('AD','Ayşe Demir','Yazılım Geliştirme','29 Kas','9 gün'),('CY','Can Yılmaz','Finans','2 Ara','12 gün')]
 c.patch(1480,624,355,392,'')
 for y,(initial,name,dept,date,days) in zip([642,735,828,921],people):
  c.draw.ellipse((1417,y,1467,y+50),fill='#e5e7eb')
  c.patch(1424,y+10,38,31,initial,18,600,INK,'#e5e7eb',align='center');c.patch(1485,y-5,265,31,name,18);c.patch(1485,y+24,265,30,dept,16,color=MUTED)
  c.patch(1760,y-3,72,27,date,16,color=MUTED,align='right');c.patch(1760,y+24,72,28,days,16,color=PURPLE,align='right')
 c.patch(1410,1010,420,15,'')
 c.save('dashboard-'+lang+'.png',lang,(0,0,1900,1025))

def invite(en):
 c=Capture('invite-source.png');lang='en' if en else 'tr'
 c.patch(73,46,650,38,'Invite Employee' if en else 'Çalışan Davet Et',22,600)
 fields=[(75,119,515,65,'Email *' if en else 'E-posta *','alex.morgan@example.com' if en else 'deniz.aksoy@example.com'),(621,119,460,65,'Start Date' if en else 'İşe Başlama Tarihi','1 Dec 2026' if en else '01.12.2026'),(75,215,470,68,'Department' if en else 'Departman','Engineering' if en else 'Yazılım Geliştirme'),(621,215,470,68,'Team' if en else 'Ekip','Platform Team' if en else 'Platform Ekibi'),(75,316,470,68,'Work Location' if en else 'Görev Yeri','Nicosia Head Office' if en else 'Lefkoşa Merkez Ofis'),(75,418,470,68,'Position' if en else 'Pozisyon','Software Engineer' if en else 'Yazılım Mühendisi'),(621,418,470,68,'Manager' if en else 'Yönetici','Emma Wilson' if en else 'Ayşe Demir')]
 for x,y,w,h,label,value in fields:
  c.patch(x+2,y+2,w-4,h-4,'')
  c.patch(x+12,y+9,w-24,20,label,13,color=MUTED);c.patch(x+12,y+31,w-24,26,value,18)
 c.patch(77,521,1057,126,'')
 c.patch(88,535,980,25,'Message' if en else 'Mesaj',15,color=MUTED)
 c.patch(88,567,1014,55,'Welcome to the team, Alex! Your first day is 1 December at 09:00.' if en else 'Aramıza hoş geldin Deniz! İlk günün 1 Aralık, saat 09.00’da.',17)
 c.patch(90,652,600,26,'Maximum 500 characters' if en else 'Maksimum 500 karakter',14,color=MUTED)
 c.patch(887,731,66,29,'Cancel' if en else 'İptal',17,600)
 c.patch(985,731,138,29,'Send Invitation' if en else 'Davet Gönder',17,600,WHITE,c.im.getpixel((984,730)),align='center')
 c.save('employee-invite-'+lang+'.png',lang,(44,22,1167,788))

def company_only(name):
 c=Capture(name+'.png');sidebar(c,False);c.save(name+'-tr.png','tr')

def calendar():
 c=Capture('leave-calendar.png');c.patch(74,24,138,29,'Dashboard',18,color=MUTED);c.patch(236,24,180,29,'Calendar',18)
 c.patch(15,120,228,62,'Calendar',44,700);c.patch(15,224,222,46,'November 2026',28,600)
 c.patch(285,225,95,37,'Today',18,color=PURPLE);c.patch(1111,128,119,34,'Public holidays',15,color=MUTED);c.patch(1257,128,125,34,'Approved leave',15,color=MUTED)
 c.patch(1417,131,105,32,'Connect',18,600);c.patch(1366,234,160,24,'View',14,color=MUTED);c.patch(1366,255,134,24,'Month',18)
 for x,day in zip([124,341,558,775,992,1209,1426],['MON','TUE','WED','THU','FRI','SAT','SUN']):c.patch(x-48,330,96,32,day,16,600,align='center')
 events=[(687,438,829,27,'James Parker · Paternity leave'),(904,473,176,27,'Sophie Turner'),(32,624,397,27,'James Parker · Paternity leave'),(470,624,175,27,'Emma Wilson'),(687,769,176,28,'Daniel Clark'),(32,923,397,27,'Olivia Taylor · Sick leave'),(904,923,393,27,'Alex Morgan · Annual leave')]
 for x,y,w,h,title in events:c.patch(x,y,w,h,title,18,600,WHITE,'#10b981')
 c.patch(1506,26,31,27,'AM',15,600,INK,'#f4f5f7',align='center')
 c.save('leave-calendar-en.png','en')

def leave_requests():
 c=Capture('leave-requests.png');sidebar(c,True,'Leaves');c.patch(410,24,139,28,'Dashboard',18,color=MUTED);c.patch(570,24,230,28,'Leaves',18)
 c.patch(350,119,850,64,'Leave Requests',44,700);c.patch(1622,132,175,31,'Create Leave Request',17,600,WHITE,'#9c76ed',align='center')
 c.patch(380,260,97,33,'All Leave',18,color=PURPLE);c.patch(502,260,230,33,'My Leave Requests',18,color=MUTED)
 for x,w,text in [(1452,82,'Refresh'),(1550,174,'Edit Columns'),(1745,110,'Download')]:c.patch(x,346,w,31,text,17,color=PURPLE)
 header='#f8f9fa'
 for x,w,text in [(370,70,'EMPLOYEE'),(518,50,'LEAVE\nTYPE'),(637,102,'START\nDATE'),(836,55,'END\nDATE'),(998,70,'DURATION'),(1080,82,'STATUS'),(1233,57,'REASON'),(1390,123,'CREATED\nON'),(1575,150,'ACTIONS')]:c.patch(x,415,w,49,text,14,color=INK,bg=header)
 names=['Sophie\nTurner','James Parker','Daniel\nClark','Emma\nWilson','Alex\nMorgan','Alex\nMorgan']
 for i,(y,name) in enumerate(zip([480,575,669,763,857,951],names)):
  c.patch(370,y,132,71,name,18);c.patch(515,y,112,71,'Annual leave',17);c.patch(998,y,70,71,('0' if i==5 else '1')+'\nday',18)
  status='Approved' if i==3 else ('Cancelled' if i==5 else 'Pending');bg='#10b981' if i==3 else ('#ff3d34' if i==5 else '#fb8c00')
  c.patch(1090,y+22,98 if i==5 else (87 if i==3 else 75),31,status,15,600,WHITE,bg,align='center')
 c.patch(1235,967,145,44,'Plans changed',17)
 c.save('leave-requests-en.png','en')

def support():
 c=Capture('support-tickets.png');sidebar(c,True,'Support Tickets');c.patch(410,24,139,29,'Dashboard',18,color=MUTED);c.patch(570,24,300,29,'Support Tickets',18)
 c.patch(350,119,830,63,'Support Tickets',44,700)
 for x,w,title in [(1349,133,'SLA Report'),(1551,132,'Ticket Settings'),(1758,97,'New Ticket')]:c.patch(x,132,w,29,title,17,600,WHITE if x==1758 else PURPLE,'#9c76ed' if x==1758 else WHITE,align='center')
 for x,w,title in [(393,50,'All'),(479,92,'Within SLA'),(600,90,'Due Soon'),(726,82,'Breached'),(842,123,'Assigned to me')]:c.patch(x,253,w,29,title,16,600 if x==393 else 400,WHITE if x==393 else INK,'#9c76ed' if x==393 else WHITE,align='center')
 for x,w,title in [(370,130,'TITLE'),(523,250,'DESCRIPTION'),(795,115,'CATEGORY'),(930,100,'STATUS'),(1057,60,'SLA'),(1140,125,'REQUESTER'),(1285,120,'ASSIGNEE'),(1416,138,'CREATED\nON'),(1594,150,'UPDATED\nON'),(1773,90,'ACTIONS')]:c.patch(x,327,w,45,title,14,bg='#f8f9fa')
 rows=[('Monitor\nwon’t turn on','Screen went off after a meeting','IT Support','Open','2 hrs\nleft','Sophie\nTurner','Ethan Reed'),('VPN\nconnection','Connection drops when working remotely','IT Support','Closed','Within\nSLA','Daniel\nClark','Ethan Reed'),('Air conditioning','Meeting room on the second floor','Facilities','Open','Overdue','Emma\nWilson','Henry Brooks'),('Payslip','Copy of the October payslip','HR','Open','1 day\nleft','James\nParker','Olivia Taylor'),('Keyboard\nissue','Several keys are not working','Hardware','Open','6 hrs\nleft','Alex\nMorgan','Ethan Reed'),('Printer\npaper jam','Printer on the third floor','Hardware','Closed','Within\nSLA','Sophie\nTurner','Henry Brooks'),('Folder\naccess','Access to the accounting folder','IT Support','Open','Overdue','Daniel\nClark','Ethan Reed')]
 for y,row in zip([388,482,576,670,764,858,952],rows):
  title,desc,cat,status,sla,name,assignee=row
  for x,w,h,text,size in [(370,140,75,title,17),(524,258,75,desc,16),(795,120,75,cat,17),(1056,70,75,sla,16),(1140,130,75,name,17),(1285,120,75,assignee,17)]:c.patch(x,y,w,h,text,size,color=MUTED if x==1056 else INK)
  c.patch(938,y+25,38 if status=='Open' else 70,26,status,15,600,WHITE,'#10b981' if status=='Open' else '#ff3d34',align='center')
 c.save('support-tickets-en.png','en')

def rooms():
 c=Capture('meeting-rooms.png');sidebar(c,True,'Meeting Rooms');c.patch(410,27,139,29,'Dashboard',18,color=MUTED);c.patch(570,27,300,29,'Meeting Rooms',18)
 c.patch(350,115,1000,63,'Meeting Rooms',44,700);c.patch(1724,121,130,32,'Add Room',18,600,WHITE,'#9c76ed',align='center')
 for x,w,title in [(380,250-225,'Rooms'),(465,144,'Reservations'),(625,160,'Equipment')]:c.patch(x,250, max(w,69),34,title,18,color=PURPLE if x==380 else MUTED)
 for x,name,location,approval in [(442,'Boardroom','2nd floor',True),(918,'Winter Garden','Ground floor, garden side',False),(1394,'Training Room','3rd floor',False)]:
  c.patch(x,392,275,40,name,23,600)
  c.patch(x+8,466,45,28,'Active',16,600,WHITE,'#14c685',align='center')
  c.patch(x+72,466,155,28,'Approval required' if approval else 'Direct booking',15,color='#dd8e17' if approval else '#09b6c9')
  c.patch(x+39,537,300,27,'Capacity',18);c.patch(x+39,565,300,27,('8' if x==442 else ('12' if x==918 else '24'))+' people',17,color=MUTED)
  c.patch(x+39,607,300,27,'Location',18);c.patch(x+39,635,300,27,location,17,color=MUTED)
  c.patch(x+39,677,316,30,'Approval required' if approval else 'Direct booking',18)
  c.patch(x+39,708,345,56,'Managers approve bookings\nbefore they are confirmed.' if approval else 'Employees can book this room\nwithout additional approval.',17,color=MUTED)
  c.patch(x+16,819,345,31,'Book Room',17,600,PURPLE,align='center')
 c.save('meeting-rooms-en.png','en')

def orgchart():
 c=Capture('orgchart.png');c.patch(48,26,180,34,'Dashboard',20,color=MUTED);c.patch(236,26,230,34,'Employees',20,color=MUTED)
 c.patch(48,82,800,61,'Employees',46,700);c.patch(72,208,170,39,'All Employees',24,color='#8057ee');c.patch(280,208,400,39,'Former Employees',24,color='#475467')
 c.patch(124,289,330,32,'Search people, job titles…',20,color='#98a2b3');c.patch(904,289,170,32,'My position',20);c.patch(1107,289,164,32,'Collapse all',20)
 people=[(680,421,'DA','David Anderson','CEO','Management'),(280,630,'OT','Olivia Taylor','HR Manager','Human Resources'),(680,630,'DC','Daniel Clark','Finance Manager','Finance'),(1080,630,'MS','Michael Scott','Engineering Lead','Engineering'),(136,842,'ST','Sophie Turner','HR Specialist','Human Resources'),(424,842,'AW','Adam White','Payroll Specialist','Human Resources'),(1080,842,'GE','Grace Evans','Software Engineer','Engineering')]
 for x,y,initial,name,title,dept in people:
  # Erase only the text areas. Keep the source node icons and connector lines.
  bg=c.im.getpixel((x-32,y-30));c.patch(x-28,y-16,56,34,initial,24,600,WHITE,bg,align='center')
  for py,w,h,text,size,color,weight in [(y+45,270,33,name,22,'#51469b',600),(y+75,270,29,title,20,INK,400),(y+103,270,28,dept,17,'#8a93a3',400)]:
   w=min(w,200) if x==136 else w
   c.patch(x-w//2,py,w,h,text,size,weight,color,'#f8f9fc',align='center')
 c.save('orgchart-en.png','en')

def payroll(en):
 c=Capture('payments.png');lang='en' if en else 'tr'
 c.patch(69,36,590,25,'Process Payroll – Engineering Team' if en else 'Bordro İşlemi – Yazılım Ekibi',13,700)
 for x,w,text in [(77,156,'Review & Validate' if en else 'Kontrol ve Doğrulama'),(322,174,'Generate Documents' if en else 'Belgeleri Oluştur'),(562,157,'Send Documents' if en else 'Belgeleri Gönder'),(811,168,'Finalize & Update Status' if en else 'Tamamla ve Güncelle')]:c.patch(x,70,w,20,text,11,color=INK if x==77 else MUTED)
 c.patch(44,113,800,26,'Step 1: Review & Validate Payroll Data' if en else 'Adım 1: Bordro Bilgilerini Kontrol Edin',14,700)
 c.patch(60,151,427,136,'')
 c.patch(65,158,400,25,'Payroll Group Details' if en else 'Ödeme Grubu Bilgileri',14,700)
 for y,text in [(188,'Group Name: Engineering Team' if en else 'Grup: Yazılım Ekibi'),(206,'Bank Account: Demo Bank' if en else 'Banka Hesabı: Demo Bank'),(224,'Account Holder: Kolik Demo' if en else 'Hesap Sahibi: Kolik Demo'),(242,'Account Number: ****7890' if en else 'Hesap Numarası: ****7890'),(260,'Currency: USD' if en else 'Para Birimi: USD')]:c.patch(65,y,400,18,text,12,color=MUTED)
 c.patch(534,159,420,24,'Payment Summary' if en else 'Ödeme Özeti',14,700);c.patch(534,184,420,33,'6,400 USD',28,600,PURPLE)
 c.patch(534,227,420,20,'Total amount for 2 employees' if en else '2 çalışan için toplam tutar',12,color=MUTED)
 c.patch(565,254,380,24,'All validations passed' if en else 'Tüm kontroller tamamlandı',12,color='#10b981')
 c.patch(63,343,851,29,'Employee Details' if en else 'Çalışan Bilgileri',14,700)
 c.patch(70,376,889,22,'',bg='#f8f9fa')
 for x,w,title in [(77,260,'EMPLOYEE' if en else 'ÇALIŞAN'),(346,216,'BANK ACCOUNT' if en else 'BANKA HESABI'),(591,100,'SALARY' if en else 'MAAŞ'),(703,135,'STATUS' if en else 'DURUM'),(851,105,'ACTIONS' if en else 'İŞLEMLER')]:c.patch(x,376,w,22,title,10,700,bg='#f8f9fa')
 for y,name in [(415,'Emma Wilson' if en else 'Ayşe Demir'),(476,'Alex Morgan' if en else 'Deniz Aksoy')]:
  c.patch(72,y,267,41,name,13);c.patch(340,y-2,224,43,'')
  c.patch(346,y+1,215,18,'Demo Bank',13);c.patch(346,y+19,215,16,'****8901',11,color=MUTED)
  c.patch(565,y,120,41,'3,200 USD',13)
  if not en:c.patch(718,y+10,28,17,'Uygun',9,600,WHITE,'#10b981',align='center')
 c.patch(758,577,210,25,'Generate Documents' if en else 'Belgeleri Oluştur',12,600,WHITE,c.im.getpixel((760,579)),align='center')
 c.patch(937,637,45,23,'Cancel' if en else 'İptal',12,color=PURPLE,align='center')
 c.save('payments-'+lang+'.png',lang)

for en in [False,True]:profile(en);dashboard(en);invite(en);payroll(en)
for name in ['leave-requests','support-tickets','meeting-rooms']:company_only(name)
calendar();leave_requests();support();rooms();orgchart()
# A language-specific social preview; the small embedded screenshot uses the same localised asset.
c=Capture('og-kolik.png');c.patch(70,126,1080,70,'HR and workplace operations, together.',45,700,bg='#f4f0fa')
leave=Image.open(OUT/'leave-requests-en.png');leave=leave.crop((320,0,leave.width,leave.height)).resize((900,586),Image.Resampling.LANCZOS)
c.im.paste(leave,(150,230));c.save('og-kolik-en.png','en')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
print('Prepared',len(manifest),'assets using fixed Inter font. No generative image processing.')
