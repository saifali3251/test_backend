-- Fieldwork Staging Baseline Data Snapshot
-- Contains production-realistic sample projects, team members, labels, and tasks.

BEGIN;

-- 1. Members
INSERT INTO members (id, name, email, role, created_at) VALUES
  (1, 'Sarah Connor', 'sarah.connor@skyline.dev', 'Tech Lead', NOW()),
  (2, 'Alex Rivera', 'alex.rivera@skyline.dev', 'Senior Backend Engineer', NOW()),
  (3, 'Maya Patel', 'maya.patel@skyline.dev', 'Frontend Architect', NOW()),
  (4, 'Liam Chen', 'liam.chen@skyline.dev', 'DevOps & Cloud Engineer', NOW()),
  (5, 'Elena Rostov', 'elena.rostov@skyline.dev', 'Product Manager', NOW())
ON CONFLICT (email) DO NOTHING;

-- 2. Labels
INSERT INTO labels (id, name, color) VALUES
  (1, 'feature', '#2563eb'),
  (2, 'bug', '#dc2626'),
  (3, 'infra', '#d97706'),
  (4, 'security', '#9333ea'),
  (5, 'performance', '#16a34a')
ON CONFLICT (name) DO NOTHING;

-- 3. Projects
INSERT INTO projects (id, name, description, status, created_at, updated_at) VALUES
  (1, 'OmniAgent Core Platform', 'Autonomous agent execution engine with CoW container sandboxing.', 'active', NOW(), NOW()),
  (2, 'Developer Console & Live Previews', 'Interactive dashboard providing instant web previews and telemetry.', 'active', NOW(), NOW()),
  (3, 'Zero-Trust VPC & Secret Vault', 'Network isolation layer with short-lived credentials and egress firewall.', 'planning', NOW(), NOW()),
  (4, 'Q3 Load Testing & Benchmarking', 'Latency and memory profiling across 500 concurrent container sandbox instances.', 'completed', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 4. Tasks
INSERT INTO tasks (id, title, description, status, priority, due_date, project_id, assignee_id, created_at, updated_at) VALUES
  (1, 'Implement CoW warm pool strike worker', 'Provision ephemeral container clones under 100ms.', 'in_progress', 'high', CURRENT_DATE + INTERVAL '3 days', 1, 2, NOW(), NOW()),
  (2, 'Stream container logs over WebSockets', 'Bidirectional log streaming directly to browser UI.', 'in_progress', 'high', CURRENT_DATE + INTERVAL '5 days', 2, 3, NOW(), NOW()),
  (3, 'Fix token refresh race condition on expired session', 'Handle simultaneous requests during OAuth token renewal.', 'todo', 'high', CURRENT_DATE + INTERVAL '2 days', 2, 1, NOW(), NOW()),
  (4, 'Audit sub-50ms snapshot restore latency', 'Profile APFS/XFS clonefile execution times under load.', 'done', 'medium', CURRENT_DATE - INTERVAL '1 day', 4, 4, NOW(), NOW()),
  (5, 'Configure WireGuard mesh for sandbox isolation', 'Egress and inter-node networking security rules.', 'todo', 'medium', CURRENT_DATE + INTERVAL '10 days', 3, 4, NOW(), NOW()),
  (6, 'Host developer UX walkthrough and review feedback', 'Review dashboard usability with platform engineers.', 'todo', 'low', CURRENT_DATE + INTERVAL '7 days', 2, 5, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 5. Task Labels (Many-to-Many)
INSERT INTO task_labels (task_id, label_id) VALUES
  (1, 1), -- Task 1: feature
  (1, 3), -- Task 1: infra
  (2, 1), -- Task 2: feature
  (2, 5), -- Task 2: performance
  (3, 2), -- Task 3: bug
  (3, 4), -- Task 3: security
  (4, 5), -- Task 4: performance
  (5, 3), -- Task 5: infra
  (5, 4), -- Task 5: security
  (6, 1)  -- Task 6: feature
ON CONFLICT DO NOTHING;

-- Sync sequences to avoid ID collisions on subsequent user inserts
SELECT setval('members_id_seq', COALESCE((SELECT MAX(id) FROM members), 1));
SELECT setval('labels_id_seq', COALESCE((SELECT MAX(id) FROM labels), 1));
SELECT setval('projects_id_seq', COALESCE((SELECT MAX(id) FROM projects), 1));
SELECT setval('tasks_id_seq', COALESCE((SELECT MAX(id) FROM tasks), 1));

COMMIT;

