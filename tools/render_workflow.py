"""Render the synthetic workflow story; Pillow is only needed to rebuild assets."""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 540
INK = '#17324D'
BLUE = '#2965D9'
TEAL = '#4F9C8E'
MUTED = '#60788B'
LINE = '#D6E2EB'
BG = '#F9FCFE'
WHITE = '#FFFFFF'


def font(size, bold=False):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype(name, size)


def centered(draw, text, x, y, size=24, fill=INK, bold=False):
    face = font(size, bold)
    width = draw.textlength(text, font=face)
    draw.text((x-width/2, y), text, font=face, fill=fill)


def icon(draw, kind, x, y, color, phase=0):
    if kind == 0:
        draw.rounded_rectangle((x-47,y-40,x+47,y+18), radius=12, outline=color, width=3)
        draw.line((x-27,y+18,x-39,y+31,x-11,y+18), fill=color, width=3)
        for i in range(11):
            height = 7 + abs(math.sin(i*1.15 + phase))*25
            bx = x-35+i*7
            draw.line((bx,y-10-height/2,bx,y-10+height/2), fill=color, width=4)
    elif kind == 1:
        draw.rectangle((x-34,y-48,x+34,y+42), outline=color, width=3)
        for i, length in enumerate([42, 29, 42, 35]):
            draw.line((x-22,y-27+i*17,x-22+length,y-27+i*17), fill=color, width=3)
    elif kind == 2:
        draw.ellipse((x-40,y-43,x+40,y+37), outline=color, width=3)
        draw.line((x-23,y-3,x-5,y+14,x+26,y-20), fill=color, width=5)
    else:
        for offset in [19, 0, -19]:
            draw.arc((x-43,y-30+offset,x+43,y-3+offset), 0, 180, fill=color, width=3)
        draw.line((x-43,y-16,x-43,y+32), fill=color, width=3)
        draw.line((x+43,y-16,x+43,y+32), fill=color, width=3)
        draw.ellipse((x-43,y-30,x+43,y-3), outline=color, width=3)


def frame(stage, phase, analysis):
    image = Image.new('RGB', (W,H), BG)
    draw = ImageDraw.Draw(image)
    draw.text((44,29), 'From conversation to business record', font=font(36,True), fill=INK)
    draw.text((44,84), 'Voice, workflows and integrations', font=font(22), fill=MUTED)
    draw.rounded_rectangle((840,80,1036,113), radius=7, fill='#E6F3EF')
    centered(draw,'Synthetic demo',938,85,18,TEAL,True)
    titles=['Request','Structured data','Human review','CRM / ERP']
    captions=['Call or message','Fields and summary','Explicit approval','Apply once']
    for i in range(4):
        x=44+i*258
        completed=i<min(stage,4)
        active=i==min(stage,3)
        color=TEAL if completed else BLUE if active else MUTED
        draw.rectangle((x,147,x+216,337), fill=WHITE, outline=color if active or completed else LINE, width=2)
        centered(draw, titles[i], x+108,162,23,color,True)
        icon(draw,i,x+108,239,color,phase if i==0 and stage==0 else 0)
        centered(draw,captions[i],x+108,302,18,MUTED)
        if i<3:
            draw.line((x+221,242,x+251,242),fill=TEAL if completed else LINE,width=2)
            draw.line((x+245,237,x+251,242,x+245,247),fill=TEAL if completed else LINE,width=2)
            if i==min(stage,2) and stage<3:
                progress=(phase/(2*math.pi))%1
                px=x+222+progress*25
                draw.ellipse((px-4,238,px+4,246),fill=BLUE)
    status=[
        ('A customer request arrives','A fictional conversation asks for a quotation.'),
        ('AI prepares a structured summary','Status: '+analysis['status']+'     Action: '+analysis['next_action']),
        ('Human review before any update','The proposed change waits for explicit approval.'),
        ('Approved update applied once','CRM record changed. The action is recorded in the audit trail.'),
        ('Duplicate delivery safely skipped','Same event, same content. No second CRM update.')
    ][stage]
    draw.line((44,368,1036,368),fill=LINE,width=2)
    draw.text((44,389),status[0],font=font(29,True),fill=TEAL if stage>=3 else INK)
    draw.text((44,434),status[1],font=font(22),fill=MUTED)
    draw.text((44,495),'Illustrated fixture-based workflow. No live providers or customer data.',font=font(18),fill=MUTED)
    return image


def main():
    analysis=json.loads((ROOT/'fixtures/model_response.json').read_text())['analysis']
    events=json.loads((ROOT/'examples/crm-events.json').read_text())
    assert [x['outcome'] for x in events]==['review','applied','duplicate','review']
    out=ROOT/'assets';out.mkdir(exist_ok=True)
    static=frame(4,0,analysis)
    static.save(out/'workflow.png',optimize=True)
    palette=Image.new('RGB',(8,1))
    palette.putdata([tuple(bytes.fromhex(c[1:])) for c in [INK,BLUE,TEAL,MUTED,LINE,BG,WHITE,'#E6F3EF']])
    palette=palette.quantize(colors=32)
    frames=[]
    for index in range(84):
        stage=min(4,int(index/84*5))
        image=frame(stage,(index%17)/17*2*math.pi,analysis)
        frames.append(image.quantize(palette=palette,dither=Image.Dither.NONE))
    frames[0].save(out/'workflow.gif',save_all=True,append_images=frames[1:],
                   duration=160,loop=0,optimize=True,disposal=2)
    print(json.dumps({'static':'assets/workflow.png','animation':'assets/workflow.gif',
                      'duration_ms':84*160,'synthetic':True,'size':[W,H]}))


if __name__=='__main__':
    main()
