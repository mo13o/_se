# API 契約摘要

所有端點前綴 `/api/v1`。登入使用 HttpOnly SameSite Cookie；變更操作必須傳送登入／註冊回應提供的 `X-CSRF-Token`。

- Auth：`/auth/register`、`/auth/login`、`/auth/logout`、`/auth/me`、`/users/me`
- 個人：`/tasks`、`/courses`、`/courses/{id}/sessions`、`/calendar/events`、`/dashboard/summary`、`/notifications`
- 團隊：`/teams`、`/teams/{id}/members`、`/teams/{id}/invites`、`/team-invites/accept`
- 專案：`/teams/{id}/projects`、`/projects/{id}`、`/projects/{id}/milestones`
- 協作：`/projects/{id}/tasks`、`/project-tasks/{id}`、`/project-tasks/{id}/status`、留言端點
- 報表：`/projects/{id}/summary`、`/projects/{id}/tasks.csv`、`/projects/{id}/reports/weekly.pdf`

完整可互動契約啟動後見 `/docs`。
