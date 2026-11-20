"""Localise text in the existing assistant demonstration; retain its shell and timing."""
from pathlib import Path
import argparse,json,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFont
ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--ffmpeg',required=True);args=ap.parse_args()
fontdir=Path(tempfile.gettempdir())/'kolik-fixed-fonts'
def font(size,weight=400):return ImageFont.truetype(str(fontdir/f'inter-latin-{weight}.ttf'),size)
def text(draw,xy,value,size=18,weight=400,fill='#101828'):draw.text(xy,value,font=font(size,weight),fill=fill,anchor='lt',spacing=6)
def wrapped(draw,xy,value,width,size=18,fill='#101828'):
 x,y=xy
 for paragraph in value.split('\n'):
  words=paragraph.split();current=''
  for word in words:
   test=(current+' '+word).strip()
   if draw.textlength(test,font=font(size))>width and current:text(draw,(x,y),current,size,fill=fill);y+=size+6;current=word
   else:current=test
  if current:text(draw,(x,y),current,size,fill=fill)
  y+=size+6
 return y
menu='Hello! How can I help?\n\nYou can ask me about:\n• Leave: balances and requests\n• Rooms: availability and bookings\n• Tasks: add, assign and complete\n• Support: IT and workplace requests\n• Performance: goals and reviews\n• Hiring: candidate and CV summaries\n\nWhat would you like to do?'
question='How much leave is left?'
def localise(image,sec):
 im=image.copy();d=ImageDraw.Draw(im)
 d.rectangle((50,5,300,39),fill='white');text(d,(52,13),'AI Assistant' if sec<2 else 'New Conversation',18,600)
 d.rectangle((22,620,425,654),fill='white');text(d,(24,630),'Type your message…',18,fill='#777777')
 if sec<2:
  d.rectangle((24,329,477,408),fill='white');text(d,(59,338),'How can I help you today?',21,600);text(d,(63,379),'Ask about your workspace.',18,fill='#777777')
 else:
  d.rectangle((0,49,493,607),fill='white')
  if sec<8:
   d.rounded_rectangle((365,75,474,122),radius=18,fill='#a172df');text(d,(385,90),'Hello!',19,fill='white')
   d.rounded_rectangle((17,135,405,598),radius=14,fill='#f5f5f5');wrapped(d,(31,151),menu,359,17)
   if sec>6:
    d.rectangle((22,620,425,654),fill='white');text(d,(24,630),question[:int((sec-6)/2*len(question))],18)
  else:
   d.rounded_rectangle((17,55,390,378),radius=12,fill='#f5f5f5')
   wrapped(d,(31,67),'• Rooms: availability and bookings\n• Tasks: add, assign and complete\n• Support: IT and workplace requests\n• Performance: goals and reviews\n• Hiring: candidate and CV summaries\n\nWhat would you like to do?',344,18)
   d.rounded_rectangle((254,391,457,438),radius=16,fill='#a172df');text(d,(266,406),question,16,fill='white')
   d.rounded_rectangle((17,452,390,585),radius=14,fill='#f5f5f5')
   wrapped(d,(31,467),'For 2026, you have 14 days of annual leave left (112 hours). You have used 6 days so far.',343,18)
 return im
w,h=508,676;fps=8
reader=subprocess.Popen([args.ffmpeg,'-loglevel','error','-i',str(args.sources/'assistant-demo.mp4'),'-vf',f'fps={fps}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
writer=subprocess.Popen([args.ffmpeg,'-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(args.output/'assistant-demo-en.mp4')],stdin=subprocess.PIPE)
frames=0
while True:
 data=reader.stdout.read(w*h*3)
 if len(data)!=w*h*3:break
 im=localise(Image.frombytes('RGB',(w,h),data),frames/fps)
 if frames==80:im.save(args.output/'assistant-demo-poster-en.png',optimize=True)
 writer.stdin.write(im.tobytes());frames+=1
reader.stdout.close();writer.stdin.close();assert reader.wait()==0;assert writer.wait()==0
p=args.output/'manifest.json';m=json.loads(p.read_text(encoding='utf8'))
for name in ['assistant-demo-en.mp4','assistant-demo-poster-en.png']:m[name]={'language':'en','font':'Inter','source':'assistant-demo.mp4','size':[w,h],'notes':'Text-localised from the supplied demonstration, preserving shell and sequence; illustrative leave values.'}
p.write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf8');print('Localised assistant video:',frames,'frames at',fps,'fps')
