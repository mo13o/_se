import {FormEvent,useEffect,useState} from 'react'
import {request} from './services/api'
import {CalendarView} from './CalendarView'
type Tab='tasks'|'courses'|'calendar'|'teams'|'project'|'notifications'
type Fields={name:string;semester:string;teacher:string;location:string;title:string;due_date:string;assignee_id:string}
type Team={id:string;name:string;role:string}
type Project={id:string;name:string;due_date:string;status:string}
type Member={user_id:string;display_name:string;email:string;role:string}
const statusLabels:Record<string,string>={todo:'待處理',in_progress:'進行中',review:'待審核',done:'已完成'}
const date=()=>new Date().toISOString().slice(0,10)
const blank=():Fields=>({name:'',semester:'115-1',teacher:'',location:'',title:'',due_date:date(),assignee_id:''})

export function Workspace({tasks}:{tasks:React.ReactNode}){
 const [tab,setTab]=useState<Tab>('tasks')
 const tabs:[Tab,string][]=[['tasks','任務'],['courses','課程'],['calendar','行事曆'],['teams','團隊'],['project','專案看板／甘特'],['notifications','通知']]
 return <><div className="workspace-nav">{tabs.map(([key,label])=><button className={tab===key?'active':''} onClick={()=>setTab(key)} key={key}>{label}</button>)}</div>{tab==='tasks'?tasks:tab==='calendar'?<CalendarView/>:<Advanced tab={tab} navigate={setTab}/>}</>
}

function Advanced({tab,navigate}:{tab:Exclude<Tab,'tasks'|'calendar'>;navigate:(tab:Tab)=>void}){
 const [data,setData]=useState<any[]>([]),[error,setError]=useState(''),[open,setOpen]=useState(false),[projectOpen,setProjectOpen]=useState(false),[saving,setSaving]=useState(false),[form,setForm]=useState<Fields>(blank())
 const [teams,setTeams]=useState<Team[]>([]),[projects,setProjects]=useState<Project[]>([]),[members,setMembers]=useState<Member[]>([]),[teamId,setTeamId]=useState(''),[projectId,setProjectId]=useState(sessionStorage.getItem('projectId')??'')
 const set=(key:keyof Fields,value:string)=>setForm(current=>({...current,[key]:value}))
 const fail=(e:unknown,message:string)=>setError(e instanceof Error?e.message:message)

 async function load(){setError('');try{
  if(tab==='courses')setData((await request<any>('/courses')).data)
  if(tab==='teams')setData((await request<any>('/teams')).data)
  if(tab==='notifications')setData((await request<any>('/notifications')).data)
  if(tab==='project')setData(projectId?(await request<any>(`/projects/${projectId}/tasks`)).data:[])
 }catch(e){fail(e,'載入失敗')}}

 useEffect(()=>{setOpen(false);setProjectOpen(false);setForm(blank());if(tab!=='project')void load()},[tab])
 useEffect(()=>{if(tab!=='project')return;void (async()=>{try{const items=(await request<{data:Team[]}>('/teams')).data;setTeams(items);const selected=items.find(t=>t.id===teamId)?.id??items[0]?.id??'';setTeamId(selected);if(!selected){setProjects([]);setProjectId('');setData([])}}catch(e){fail(e,'載入團隊失敗')}})()},[tab])
 useEffect(()=>{if(tab!=='project'||!teamId)return;void (async()=>{try{const [items,people]=await Promise.all([request<{data:Project[]}>(`/teams/${teamId}/projects`),request<{data:Member[]}>(`/teams/${teamId}/members`)]);setProjects(items.data);setMembers(people.data);const saved=sessionStorage.getItem('projectId')??'';const selected=items.data.find(p=>p.id===projectId||p.id===saved)?.id??items.data[0]?.id??'';setProjectId(selected);if(selected)sessionStorage.setItem('projectId',selected);else sessionStorage.removeItem('projectId')}catch(e){fail(e,'載入專案或成員失敗')}})()},[tab,teamId])
 useEffect(()=>{if(tab==='project')void load()},[tab,projectId])

 async function add(e:FormEvent){e.preventDefault();setSaving(true);setError('');try{
  if(tab==='courses')await request('/courses',{method:'POST',body:JSON.stringify({name:form.name,semester:form.semester,teacher:form.teacher,location:form.location,color:'#315fd2'})})
  if(tab==='teams')await request('/teams',{method:'POST',body:JSON.stringify({name:form.name,description:''})})
  if(tab==='project'&&projectId)await request(`/projects/${projectId}/tasks`,{method:'POST',body:JSON.stringify({title:form.title,description:'',priority:'medium',status:'todo',start_date:date(),due_date:form.due_date,estimated_hours:null,assignee_id:form.assignee_id||null})})
  setForm(blank());setOpen(false);await load()
 }catch(e){fail(e,'新增失敗')}finally{setSaving(false)}}

 async function createProject(e:FormEvent){e.preventDefault();if(!teamId)return;setSaving(true);setError('');try{
  const result=await request<{data:{id:string;name:string}}>(`/teams/${teamId}/projects`,{method:'POST',body:JSON.stringify({name:form.name,description:'',start_date:date(),due_date:form.due_date,status:'active'})})
  const items=(await request<{data:Project[]}>(`/teams/${teamId}/projects`)).data;setProjects(items);setProjectId(result.data.id);sessionStorage.setItem('projectId',result.data.id);setForm(blank());setProjectOpen(false)
 }catch(e){fail(e,'建立專案失敗')}finally{setSaving(false)}}

 const heading=tab==='courses'?'課程與課表':tab==='teams'?'我的團隊':tab==='project'?'專案看板與甘特圖':'通知中心'
 return <main className="advanced"><div className="heading"><h1>{heading}</h1><div className="actions">
  {tab==='project'&&<button onClick={()=>{setProjectOpen(!projectOpen);setOpen(false)}} disabled={!teamId}>{projectOpen?'取消':'建立專案'}</button>}
  {['courses','teams','project'].includes(tab)&&<button className="primary" onClick={()=>{setOpen(!open);setProjectOpen(false)}} disabled={tab==='project'&&!projectId}>{open?'取消':tab==='project'?'新增任務':'新增'}</button>}
 </div></div>
 {error&&<div className="notice error">{error}</div>}
 {tab==='project'&&teams.length===0&&<div className="notice error">尚未建立團隊。<button onClick={()=>navigate('teams')}>前往建立團隊</button></div>}
 {tab==='project'&&teams.length>0&&<div className="project-selectors"><label>團隊<select value={teamId} onChange={e=>setTeamId(e.target.value)}>{teams.map(team=><option key={team.id} value={team.id}>{team.name}</option>)}</select></label><label>專案<select value={projectId} onChange={e=>{setProjectId(e.target.value);sessionStorage.setItem('projectId',e.target.value)}}><option value="">請選擇專案</option>{projects.map(project=><option key={project.id} value={project.id}>{project.name}</option>)}</select></label>{projects.length===0&&<small>這個團隊尚無專案，請按「建立專案」。</small>}</div>}
 {projectOpen&&<form className="panel advanced-form" onSubmit={createProject}><h2>建立專案</h2><label>專案名稱<input required value={form.name} onChange={e=>set('name',e.target.value)}/></label><label>截止日期<input required type="date" min={date()} value={form.due_date} onChange={e=>set('due_date',e.target.value)}/></label><button className="primary" disabled={saving}>{saving?'建立中…':'建立專案'}</button></form>}
 {open&&<form className="panel advanced-form" onSubmit={add}>
  {tab==='courses'&&<><label>課程名稱<input required value={form.name} onChange={e=>set('name',e.target.value)}/></label><div className="row"><label>學期<input required value={form.semester} onChange={e=>set('semester',e.target.value)}/></label><label>教師<input value={form.teacher} onChange={e=>set('teacher',e.target.value)}/></label></div><label>地點<input value={form.location} onChange={e=>set('location',e.target.value)}/></label></>}
  {tab==='teams'&&<label>團隊名稱<input required value={form.name} onChange={e=>set('name',e.target.value)}/></label>}
  {tab==='project'&&<><label>任務名稱<input required value={form.title} onChange={e=>set('title',e.target.value)}/></label><label>負責人<select value={form.assignee_id} onChange={e=>set('assignee_id',e.target.value)}><option value="">尚未指派</option>{members.map(member=><option key={member.user_id} value={member.user_id}>{member.display_name}（{member.role}）</option>)}</select></label><label>截止日期<input required type="date" value={form.due_date} onChange={e=>set('due_date',e.target.value)}/></label></>}
  <button className="primary" disabled={saving}>{saving?'儲存中…':'儲存'}</button>
 </form>}
 <div className={tab==='project'?'board':'advanced-list'}>{data.map(item=><article key={item.id} className="advanced-card"><h3>{item.name||item.title||item.message}</h3>{item.status&&<span className="status-label">{statusLabels[item.status]??item.status}</span>}{item.due_date&&<p>截止：{item.due_date}</p>}{tab==='project'&&<label className="assignee-field">負責人<select aria-label={`${item.title}的負責人`} value={item.assignee_id||''} onChange={async e=>{setError('');try{await request(`/project-tasks/${item.id}`,{method:'PATCH',body:JSON.stringify({assignee_id:e.target.value||null})});await load()}catch(error){fail(error,'指派失敗')}}}><option value="">尚未指派</option>{members.map(member=><option key={member.user_id} value={member.user_id}>{member.display_name}</option>)}</select></label>}{item.role&&<p>角色：{item.role}</p>}{tab==='project'&&<div className="actions status-actions">{['todo','in_progress','review','done'].map(status=><button className={item.status===status?'active':''} key={status} onClick={async()=>{await request(`/project-tasks/${item.id}/status`,{method:'PATCH',body:JSON.stringify({status})});await load()}}>{statusLabels[status]}</button>)}</div>}</article>)}</div>
 {data.length===0&&tab!=='project'&&<p className="state">目前沒有資料</p>}
 {tab==='project'&&projectId&&data.length===0&&<p className="state">這是一個空白專案。請先建立第一個任務，之後才會提供 CSV 與 PDF 週報。</p>}
 {tab==='project'&&projectId&&data.length>0&&<div className="actions"><a href={`${import.meta.env.VITE_API_BASE_URL??'http://127.0.0.1:8000'}/api/v1/projects/${projectId}/tasks.csv`}>下載 CSV</a><a href={`${import.meta.env.VITE_API_BASE_URL??'http://127.0.0.1:8000'}/api/v1/projects/${projectId}/reports/weekly.pdf?from=2026-01-01&to=2026-12-31`}>下載 PDF 週報</a></div>}
 </main>
}
