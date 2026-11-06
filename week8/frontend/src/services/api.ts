import type {Filters,Summary,Task,TaskInput} from '../types/task'
let csrf=sessionStorage.getItem('csrf')??''
const base=import.meta.env.VITE_API_BASE_URL??'http://127.0.0.1:8000'
export async function request<T>(path:string,options?:RequestInit):Promise<T>{const method=options?.method??'GET';const response=await fetch(`${base}/api/v1${path}`,{...options,credentials:'include',headers:{'Content-Type':'application/json',...(method!=='GET'?{'X-CSRF-Token':csrf}:{}),...options?.headers}});if(response.status===204)return undefined as T;const body=await response.json();if(!response.ok)throw new Error(body.error?.message??body.detail?.message??body.detail??'操作失敗');return body}
export async function listTasks(filters:Filters){const query=new URLSearchParams();Object.entries(filters).forEach(([k,v])=>{if(v)query.set(k,v)});return request<{data:Task[];meta:{total:number}}>(`/tasks?${query}`)}
export async function getSummary(){return (await request<{data:Summary}>('/dashboard/summary')).data}
export async function createTask(input:TaskInput){return (await request<{data:Task}>('/tasks',{method:'POST',body:JSON.stringify(input)})).data}
export async function updateTask(id:string,input:Partial<TaskInput>){return (await request<{data:Task}>(`/tasks/${id}`,{method:'PATCH',body:JSON.stringify(input)})).data}
export async function deleteTask(id:string){return request<void>(`/tasks/${id}`,{method:'DELETE'})}
export async function currentUser(){const r=await request<{data:{id:string;email:string;display_name:string};csrf_token:string}>('/auth/me');csrf=r.csrf_token;sessionStorage.setItem('csrf',csrf);return r.data}
export async function authenticate(mode:'login'|'register',email:string,password:string,display_name=''){const r=await request<{data:{id:string;email:string;display_name:string};csrf_token:string}>(`/auth/${mode}`,{method:'POST',body:JSON.stringify(mode==='register'?{email,password,display_name}:{email,password})});csrf=r.csrf_token;sessionStorage.setItem('csrf',csrf);return r.data}
export async function logout(){await request<void>('/auth/logout',{method:'POST'});csrf='';sessionStorage.removeItem('csrf')}
export async function listCourses(){return request<{data:Array<{id:string;name:string;semester:string;teacher:string;location:string;color:string}>}>('/courses')}
export async function createCourse(input:{name:string;semester:string;teacher:string;location:string;color:string}){return request('/courses',{method:'POST',body:JSON.stringify(input)})}

