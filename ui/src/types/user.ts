import { SharePermissions, UserOptions } from './api';

export interface UserServer {
  name: string;
  last_activity: string;
  started: string;
  pending: boolean | null;
  ready: boolean;
  stopped: boolean;
  url: string;
  user_options: UserOptions | Record<string, unknown>;
  progress_url: string;
}

export interface UserState {
  username: string | undefined;
  admin: boolean;
  auth_state: string | null;
  created: string | null;
  groups: string[];
  kind: string | null;
  last_activity: string | null;
  name: string;
  pending: boolean | null;
  roles: string[];
  scopes: string[];
  server: string | null;
  servers: Record<string, UserServer>;
  session_id: string | null;
  share_permissions: SharePermissions;
}
