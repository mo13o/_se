import {cleanup,render,screen,waitFor} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {afterEach,beforeEach,expect,test,vi} from 'vitest'
import {App} from './App'
afterEach(()=>cleanup())
const task={id:'1',title:'資料庫作業',description:'SQL',category:'assignment',priority:'high',status:'todo',due_date:'2026-11-01',created_at:'',updated_at:'',completed_at:null}
beforeEach(()=>{vi.stubGlobal('fetch',vi.fn((url:string,options?:RequestInit)=>{if(url.includes('/dashboard/summary'))return Promise.resolve({ok:true,json:async()=>({data:{total:1,todo:1,done:0,overdue:0,due_soon:1,completion_rate:0}})});if(options?.method==='POST')return Promise.resolve({ok:true,json:async()=>({data:task})});return Promise.resolve({ok:true,json:async()=>({data:[task],meta:{total:1}})})}))})
test('renders real task list and dashboard summary',async()=>{render(<App/>);expect(await screen.findByText('資料庫作業')).toBeInTheDocument();expect(screen.getByText('1 筆結果')).toBeInTheDocument();expect(screen.getByText('三日內')).toBeInTheDocument()})
test('submits a new task through API',async()=>{const user=userEvent.setup();render(<App/>);await screen.findByText('資料庫作業');await user.type(screen.getByLabelText('任務名稱'),'新作業');await user.click(screen.getByRole('button',{name:'新增任務'}));await waitFor(()=>expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/tasks'),expect.objectContaining({method:'POST'})))})

