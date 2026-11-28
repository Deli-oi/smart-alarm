import json,sys
shared={
"readings":{"cite":"Daniel 7 and Luke 21","gist":"Sample placeholder. The real app fetches the day's Mass readings at 6:00 and shows a short summary here, with the full citation."},
"flag":None,
"articles":[
 {"tag":"Missed news, sample copy","title":"Why central banks watch the job market","body":["A central bank cares about jobs because wages feed into prices. When hiring is strong and workers are scarce, employers pay more, and that tends to push inflation up.","So a surprisingly strong jobs report can move interest rate expectations even when nothing else has changed."]},
 {"tag":"Research in today\u2019s field, sample copy","title":"Retrieval practice beats rereading","body":["In a well-known 2006 study, Roediger and Karpicke had students read a passage and then either reread it or take a recall test on it.","A week later, the students who had been tested remembered more than the students who had reread. Pulling a fact out of memory strengthens it more than seeing it again.","This is the idea behind the morning recall gate."]},
 {"tag":"Wildcard, sample copy","title":"The Antikythera mechanism","body":["Divers found this corroded bronze device in a shipwreck off the Greek island of Antikythera in 1901.","It dates to roughly the second or first century BC. It used a train of gears to model the motions of the sun and moon and to predict eclipses.","Nothing of comparable complexity appears in the record for well over a thousand years afterwards."]}],
"quiz":[
 {"q":"What did central banks watch because wages feed into prices?","o":["The job market","Rainfall","Stock splits","Shipping rates"],"a":0},
 {"q":"Strong hiring tends to push inflation which way?","o":["Down","Up","No effect","Only on weekends"],"a":1},
 {"q":"In the 2006 study, what did one group do after reading?","o":["Took a recall test","Slept","Highlighted","Left the room"],"a":0},
 {"q":"A week later, who remembered more?","o":["The rereaders","The tested group","Both the same","Neither"],"a":1},
 {"q":"Why does retrieval practice work?","o":["It is quicker","Pulling a fact from memory strengthens it","It is more fun","It avoids notes"],"a":1},
 {"q":"Where was the Antikythera mechanism found?","o":["A Greek shipwreck","An Egyptian tomb","A Roman villa","A Turkish library"],"a":0},
 {"q":"What did it predict?","o":["Harvests","Eclipses","Wars","Tides only"],"a":1},
 {"q":"When was it found?","o":["1801","1901","1951","2001"],"a":1}]}
sample=dict(shared,audio="https://platform.r2.fish.audio/tasks/2026-11-27/23f0e03461004d938d91794d86df386e.mp3",date="Friday, 27 November",name="Eli",mode="Sample content",badge="Preview",
 events=[{"start":"08:00","end":"09:30","title":"Morning block","note":"Deep work"},
 {"start":"10:00","end":"11:50","title":"Lecture","note":""},
 {"start":"12:00","end":"13:30","title":"Lunch with a friend","note":""},
 {"start":"14:00","end":"15:50","title":"Study session","note":"Library"},
 {"start":"17:00","end":"18:00","title":"Gym","note":""}],
 mail=[{"from":"A recruiter","subject":"Interview scheduling","why":"Needs a reply"},{"from":"A club","subject":"Annual meeting Tuesday","why":""},{"from":"A friend","subject":"Weekend plans","why":""}],
 files=[{"title":"Applications tracker","kind":"Spreadsheet","when":"Mon"},{"title":"Project notes","kind":"Document","when":"Sat"},{"title":"Meeting summary","kind":"Markdown","when":"Fri"}],
 evening=[{"t":"Ship the preview","done":True,"src":"Detected: commit in your repository"},{"t":"Reply to the recruiter","done":False,"src":"No sent mail found"},{"t":"Read the chapter","done":True,"src":"Detected: Claude chat on the topic"}])
tpl=open("template.html").read()
def out(path,d):open(path,"w").write(tpl.replace("/*DATA*/null",json.dumps(d)))
out("../site/index.html",sample)

# --- everything the Home Screen install needs, written alongside the page
import os,shutil
os.makedirs("../site/assets",exist_ok=True)
for n in (180,192,512):
    shutil.copyfile(f"assets/icon-{n}.png",f"../site/assets/icon-{n}.png")

open("../site/manifest.webmanifest","w").write(json.dumps({
 "name":"Wake-Up","short_name":"Wake-Up","start_url":".","scope":".",
 "display":"standalone","orientation":"portrait",
 "background_color":"#f6f0e3","theme_color":"#f6f0e3",
 "description":"The morning issue, the recall gate, the day log.",
 "icons":[{"src":"assets/icon-192.png","sizes":"192x192","type":"image/png"},
          {"src":"assets/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"}]
},indent=1))

# Network first, cache as a fallback. The other way round would serve a stale app for days,
# and this page changes more often than it is opened.
open("../site/sw.js","w").write("""const C='wake-up-v1';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET'||u.origin!==location.origin)return;   // never touch the API
  e.respondWith(
    fetch(e.request).then(r=>{
      const copy=r.clone();
      caches.open(C).then(c=>c.put(e.request,copy)).catch(()=>{});
      return r;
    }).catch(()=>caches.match(e.request).then(r=>r||caches.match('index.html')))
  );
});
""")
