# TinyIOU - The Social Ledger of Light

**TinyIOU** is a social gratitude ledger that goes beyond likes and comments. It's a permanent digital archive for the invisible ripples we create in each other's lives — measuring **Presence, Resilience, and Radiance**.

> "Traditional social media measures attention and envy. TinyIOU measures Presence, Resilience, and Radiance."

---

## What is TinyIOU?

TinyIOU is a **protocol for human connection**. It's not about debts to be paid — it's about **ripples to be acknowledged**. Every small act of kindness, courage, and creative contribution gets memorialized in a permanent ledger.

The smallest acts of kindness, courage, and creative alchemy are recorded forever. We call these **IOUs** — not as debts to be paid, but as ripples to be acknowledged.

---

## Features

### 1. User Authentication

| Feature | Description |
|---------|-------------|
| **Email/Password Login** | Traditional authentication via Supabase |
| **Magic Link Login** | Passwordless email authentication (OTP) |
| **Password Reset** | Self-service password recovery |
| **Session Management** | Persistent sessions with secure tokens |

### 2. IOU/Gratitude Ledger (Core Feature)

The heart of TinyIOU — creating and tracking gratitude notes:

| Feature | Description |
|---------|-------------|
| **Create IOU** | Record a gratitude moment for someone |
| **IOU Categories** | Tag with attributes: |
| | • **Radiance** — Joy/light you brought |
| | • **Power** — Impact/influence |
| | • **Presence** — Being there for someone |
| | • **Grit** — Determination |
| | • **Loyalty** — Steadfast support |
| | • **Curiosity** — Seeking learning |
| | • **Bliss** — Pure joy moments |
| | • **Courage** — Brave actions |
| | • **Humility** — Grace |
| | • **Patience** — Giving space to grow |
| **Ripple Tracking** | Count how many ripples/responses an IOU generates |
| **Feed View** | Chronological wall of all IOUs |
| **Public/Private** | Control visibility of IOUs |

### 3. Social Features

| Feature | Description |
|---------|-------------|
| **User Profiles** | Customizable public user pages |
| **Friend System** | Add, request, accept friend connections |
| **Block Users** | Privacy controls to block unwanted connections |
| **Chat/Messaging** | Real-time direct messaging between users |
| **Activity Feed** | Wall showing recent IOUs from your network |

### 4. Profile Customization

| Feature | Description |
|---------|-------------|
| **Avatar Upload** | Profile picture with camera capture option |
| **Display Name** | Custom username |
| **Bio** | Short personal description |
| **Public Profile** | Profile page viewable by others |

### 5. Notifications System

Real-time notification center with alerts for:
- New IOUs received
- Friend requests
- Chat messages
- Profile visits

### 6. Admin Panel

- User management
- Content moderation
- Platform statistics

### 7. Privacy & Legal

- **Cookie Consent** — GDPR-compliant consent banner
- **Privacy Policy** — Data handling disclosure
- **Terms of Service** — Platform rules and guidelines

---

## Technical Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18** | UI library |
| **Tailwind CSS** | Styling framework |
| **Phosphor Icons** | Icon library |
| **Animate.css** | Animations |
| **Google Fonts** | Outfit + Plus Jakarta Sans |

### Backend (Supabase)

| Service | Purpose |
|---------|---------|
| **PostgreSQL** | Database |
| **Authentication** | User auth (email, magic links, OTP) |
| **Real-time** | Live subscriptions for chat/notifications |
| **Storage** | Avatar/image storage |

### Design

- Mobile-first responsive design
- Vibrant orange (#f97316) brand color
- Glassmorphism effects
- Smooth animations

---

## Pages

| Page | File | Description |
|------|------|-------------|
| **Home/Wall** | `index.html` | Main feed of IOUs |
| **Authentication** | `auth.html` | Login/Signup |
| **Profile** | `profile.html` | User profile editor |
| **Chat** | `chat.html` | Messaging interface |
| **Notifications** | `notifications.html` | Alert center |
| **About** | `about.html` | Philosophy/mission |
| **Privacy** | `privacy.html` | Privacy policy |
| **Terms** | `terms.html` | Terms of service |
| **Admin** | `admin.html` | Admin dashboard |

---

## Database Schema

### Users Table
```
- id (UUID)
- username
- email
- avatar_url
- bio
- created_at
```

### IOU Table
```
- id (UUID)
- creator_id (FK to users)
- receiver_id (FK to users)
- content (text)
- category (enum)
- visibility (public/private)
- created_at
```

### Messages Table
```
- id (UUID)
- sender_id (FK to users)
- receiver_id (FK to users)
- content (text)
- read (boolean)
- created_at
```

### Friends Table
```
- user_id (FK to users)
- friend_id (FK to users)
- status (pending/accepted/blocked)
```

### Notifications Table
```
- id (UUID)
- user_id (FK to users)
- type (IOU/friend/message)
- content (text)
- read (boolean)
- created_at
```

---

## How It Works

1. **Sign Up** — Create account via email or magic link
2. **Create IOU** — Record a gratitude moment for someone
3. **Network Grows** — Add friends to see their IOUs
4. **Build Ledger** — Accumulate a history of positive ripples
5. **Track Impact** — See how your IOUs resonate (ripples)

---

## The Philosophy

> "Traditional social media measures attention and envy. TinyIOU measures Presence, Resilience, and Radiance."

TinyIOU is not about debts to be paid — it's about **ripples to be acknowledged**. Every small act of kindness, courage, and creative contribution gets memorialized in a permanent ledger.

---

## License

This is a mirrored/study version for educational purposes. Not affiliated with the original tinyiou.com.

---

*Built with love, light, and gratitude.*
