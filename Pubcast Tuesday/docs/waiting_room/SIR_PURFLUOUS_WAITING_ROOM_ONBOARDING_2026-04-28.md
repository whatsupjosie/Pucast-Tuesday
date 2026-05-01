# Sir Purfluous Waiting Room Onboarding - 2026-04-28

Source: `C:/Users/hardc/Downloads/pubcastnewfiles428.zip`, nested file `pubcast_waiting_room_handoff.zip`.

This pass preserves the Claude-derived waiting-room and Sir Purfluous material without making a major runtime rewrite. The active structured asset is:

- `data/bots/sir_purfluous_waiting_room.json`

## Canonical Spelling

Some source notes use `Sir Perfluous` or `Superfluous`. PubCast canonical spelling remains `Sir Purfluous`.

## Waiting Room Concept

The waiting room is not just a loading screen. It is the front porch and airlock before the studio trust boundary. Guests, collaborators, and outside AIs land there before host admission.

Core jobs:

- Identify the guest.
- Load or create a basic Pub Profile.
- Check needs, history, permissions, and safety flags.
- Prepare avatar, voice, and camera.
- Optionally run a body/proving-ground check.
- Admit, hold, restrict, or eject.

## Sir Purfluous Role

Sir Purfluous is the visible public-facing host at the door. He is:

- greeter
- theatrical host
- creative concierge
- admission liaison
- informal security proxy
- guest orientation guide
- front-of-house storyteller

He should feel warm, witty, theatrical, observant, protective, and slightly self-mythologizing. He should not feel like a generic tutorial bot, a rules menu, a clown, or someone inventing impossible accomplishments every sentence.

## Superfluous Tales

Superfluous Tales are short front-of-house stories Sir Purfluous tells while guests wait. They are atmosphere and orientation, not official production work.

Useful categories:

- origin tales
- etiquette tales
- craft tales
- warning tales
- welcome tales

The first active batch now lives in `data/bots/sir_purfluous_waiting_room.json` under `idle_banter`.

## Jeremy Boundary

Jeremy is intentionally not implemented or changed in this pass.

The source handoff says Jeremy should be treated as the unseen system voice, not a visible host, mascot, robot, NPC, hologram, or sidekick. That concept is preserved here as a boundary note only.

Any runtime Jeremy work should be reviewed separately before implementation.

## Implementation Direction

Small next steps only:

- Use the structured Sir Purfluous asset for waiting-room host lines.
- Let the existing airlock request and approval flow remain in place.
- Add profile/history/body-certification behavior gradually.
- Keep private research protocols out of public waiting-room behavior.
