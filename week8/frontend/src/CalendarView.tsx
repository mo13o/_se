import {useEffect,useMemo,useState} from 'react'
import {request} from './services/api'

type CalendarEvent={id:string;type:'task'|'course';title:string;date?:string;status?:string;weekday?:number;start_time?:string;end_time?:string}
const weekdays=['日','一','二','三','四','五','六']
const statusText:Record<string,string>={todo:'待處理',done:'已完成'}
const iso=(value:Date)=>`${value.getFullYear()}-${String(value.getMonth()+1).padStart(2,'0')}-${String(value.getDate()).padStart(2,'0')}`

export function CalendarView(){
 const [cursor,setCursor]=useState(()=>new Date(new Date().getFullYear(),new Date().getMonth(),1))
 const [events,setEvents]=useState<CalendarEvent[]>([]),[error,setError]=useState(''),[selected,setSelected]=useState<CalendarEvent|null>(null)
 const cells=useMemo(()=>{const first=new Date(cursor.getFullYear(),cursor.getMonth(),1),start=new Date(first);start.setDate(1-first.getDay());return Array.from({length:42},(_,index)=>{const value=new Date(start);value.setDate(start.getDate()+index);return value})},[cursor])
 useEffect(()=>{const from=iso(cells[0]),to=iso(cells[cells.length-1]);setError('');void request<{data:CalendarEvent[]}>(`/calendar/events?from=${from}&to=${to}`).then(result=>setEvents(result.data)).catch(e=>setError(e instanceof Error?e.message:'行事曆載入失敗'))},[cells])
 const eventsFor=(day:Date)=>events.filter(event=>event.type==='task'?event.date===iso(day):event.weekday===(day.getDay()===0?7:day.getDay()))
 const move=(months:number)=>setCursor(value=>new Date(value.getFullYear(),value.getMonth()+months,1))
 return <main className="advanced calendar-page">
  <div className="heading"><div><h1>行事曆</h1><p>課程時段與個人任務截止日</p></div><div className="actions"><button onClick={()=>move(-1)}>上個月</button><button onClick={()=>setCursor(new Date(new Date().getFullYear(),new Date().getMonth(),1))}>今天</button><button onClick={()=>move(1)}>下個月</button></div></div>
  {error&&<div className="notice error">{error}</div>}
  <h2 className="calendar-title">{cursor.getFullYear()} 年 {cursor.getMonth()+1} 月</h2>
  <div className="calendar-grid">{weekdays.map(day=><div className="calendar-weekday" key={day}>週{day}</div>)}{cells.map(day=>{const outside=day.getMonth()!==cursor.getMonth(),today=iso(day)===iso(new Date());return <section className={`calendar-day${outside?' outside':''}${today?' today':''}`} key={iso(day)}><strong>{day.getDate()}</strong><div className="calendar-events">{eventsFor(day).map((event,index)=><button className={`calendar-event ${event.type}`} key={`${event.id}-${index}`} onClick={()=>setSelected({...event,date:iso(day)})}><span>{event.type==='course'?'課程':'任務'}</span>{event.title}</button>)}</div></section>})}</div>
  <div className="calendar-legend"><span><i className="task-dot"/>任務截止</span><span><i className="course-dot"/>每週課程</span></div>
  {selected&&<div className="calendar-detail panel"><div className="heading"><h2>{selected.title}</h2><button onClick={()=>setSelected(null)}>關閉</button></div><p>類型：{selected.type==='course'?'課程':'個人任務'}</p><p>日期：{selected.date}</p>{selected.type==='course'?<p>時間：{selected.start_time}–{selected.end_time}</p>:<p>狀態：{statusText[selected.status??'']??selected.status}</p>}</div>}
 </main>
}
