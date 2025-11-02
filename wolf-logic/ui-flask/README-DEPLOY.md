# Deployment Instructions

## Step 1: Stop the existing OpenMemory stack

```bash
cd /mnt/s/wolf-logic/wolf-logic
docker compose down
```

## Step 2: Start the new Flask UI stack

```bash
cd /mnt/s/wolf-logic/wolf-logic/ui-flask
docker compose up --build -d
```

## Step 3: Access the UI

- UI: http://localhost:3000
- Backend API: http://localhost:8765

## To stop this stack later:

```bash
cd /mnt/s/wolf-logic/wolf-logic/ui-flask
docker compose down
```

## To view logs:

```bash
cd /mnt/s/wolf-logic/wolf-logic/ui-flask
docker compose logs -f wolf-logic_ui
```

That's it.
