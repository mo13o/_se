export type Category='assignment'|'exam'|'project'|'other'
export type Priority='high'|'medium'|'low'
export type Status='todo'|'done'
export type Task={id:string;title:string;description:string;category:Category;priority:Priority;status:Status;due_date:string;created_at:string;updated_at:string;completed_at:string|null}
export type TaskInput=Pick<Task,'title'|'description'|'category'|'priority'|'status'|'due_date'>
export type Summary={total:number;todo:number;done:number;overdue:number;due_soon:number;completion_rate:number}
export type Filters={search:string;category:string;status:string;priority:string;sort:string}
