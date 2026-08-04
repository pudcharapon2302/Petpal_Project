# Petpal AI Design System Specification

Version: 1.1
Status: Active
Scope: All customer-facing Django templates, authentication overlays, emails where applicable, and future UI work.

## Aesthetic direction: Community Rescue Noticeboard

Petpal must feel like a thoughtfully maintained neighborhood rescue board, not a generic AI product. The visual language combines warm recycled paper, dark printer ink, vermilion notices, and a restrained teal utility accent.

- Display type uses Kodchasan; body and UI type use Bai Jamjuree.
- Cards use visible ink borders and offset print-like shadows.
- Atmosphere comes from a quiet paper grid, not blurred gradient blobs.
- Orange is decisive and dominant; teal appears only for AI or utility actions.
- Purple-on-white gradients, glassmorphism, double-sided neumorphic shadows, and generic floating blobs are prohibited.
- Motion is organized as one staggered page entrance plus purposeful state changes.
- Layouts may be asymmetrical when content benefits, but spacing and alignment stay on the shared rhythm.

## 1. Goals

- Every page must look and behave as one product.
- Layout must remain readable from 320 px mobile screens through desktop.
- Components must use shared tokens instead of one-off colors, shadows, radii, and spacing.
- Thai and English content must not change component dimensions unexpectedly.
- Accessibility, privacy notices, empty states, loading states, and error states are first-class UI.

## 2. Design principles

1. Warm, calm, trustworthy: orange is an accent, not a full-page fill.
2. Content before decoration: shadows are subtle and never define layout.
3. Predictable actions: primary action is orange, destructive action is red, neutral action is white or gray.
4. Progressive disclosure: secondary details appear after the main identity, status, and action.
5. Mobile-first proportions: no fixed card width that can shrink to text content.

## 3. Tokens

The source of truth is `myapp/static/css/petpal-design-system.css`.

### Color

- Brand 50: `#fff7ed`
- Brand 100: `#ffedd5`
- Brand 200: `#fed7aa`
- Brand 500: `#f97316`
- Brand 600: `#ea580c`
- Brand 700: `#c2410c`
- Ink: `#111827`
- Muted text: `#64748b`
- Border: `#e5e7eb`
- Surface: `#ffffff`
- Canvas: `#fffaf5`

Status colors may use green for success, red for destructive/lost alerts, blue for information, and amber for pending. Status color must never be the only indicator; include text or an icon.

### Radius

- Small controls: 12 px
- Standard containers: 18 px
- Cards and overlays: 24 px
- Pills and status chips: 999 px

### Spacing

Use a 4 px base rhythm. Preferred values: 4, 8, 12, 16, 24, 32, 48, 64, and 88 px.
Normal card gap is 24 px. Normal section gap is responsive from 48 to 88 px.

### Shadows

Use shared offset print shadows. Avoid glows, double-sided neumorphism, and large diffuse shadows. A two-pixel ink border plus a short hard shadow is the standard card treatment.

## 4. Layout standards

- Marketing/Homepage: max width 1152 px.
- Lists, maps, and dashboards: max width 1280 px.
- Forms, detail pages, profile content: max width 1024 px.
- Chat workspaces: max width 1280 px and may use viewport height.
- Horizontal gutter: 16 px minimum, scaling to 32 px.
- Every `main` must have `width: 100%` and `min-width: 0`.
- Page sections use 48-88 px vertical separation.
- Grids use `minmax(0, 1fr)` or `minmax(min(100%, 260px), 1fr)`; never size cards from text width.

## 5. Typography

- Display font: Kodchasan, stored locally.
- Body and UI font: Bai Jamjuree, stored locally.
- H1: 32-64 px depending on page type.
- H2: 24-36 px.
- H3: 18-24 px.
- Body: 16 px.
- Supporting text: 14 px.
- Labels and metadata: 12-14 px.
- Line-height: headings 1.25, body 1.6.
- Avoid all-caps for Thai text.

## 6. Components

### Navigation

One shared navbar on every interactive page. Desktop and mobile must expose the same destinations. Selected language and authentication status must be visible.

### Buttons

- Minimum interactive height: 44 px.
- One primary action per panel.
- Primary: orange background and white text.
- Secondary: white background, gray border, dark text.
- Destructive: red and requires confirmation.
- Disabled: visually muted and non-interactive.

### Cards

Standard card: white surface, 1 px border, 24 px radius, small shadow. Interactive cards may rise 3 px on hover. Missing images use a branded placeholder with the same aspect ratio as real images.

### Forms

Controls are full width, at least 48 px high, with 12 px radius. Labels appear above controls. Help text follows the field. Errors appear immediately below the field in red and are announced semantically. Long forms are grouped into named sections.

### Maps and location privacy

Maps use Leaflet and OpenStreetMap. Exact residential coordinates should not be encouraged. The form recommends nearby landmarks. Publishing coordinates requires an explicit acknowledgement. Only coordinates required for the listing are sent to the tile service; account name and phone are not included.

### Empty, loading, and error states

Each data region must define all three states. Empty states use a dashed brand border, a short explanation, and at most one primary action. Loading states preserve final layout dimensions. Errors explain recovery.

### Overlays

Authentication and confirmation overlays use a maximum width of 480 px, 24 px radius, large shadow, accessible focus handling, escape-to-close where safe, and scrollable content on small screens.

## 7. Responsive behavior

- 320-639 px: one-column cards, full-width primary buttons.
- 640-1023 px: two-column card grids when useful.
- 1024-1279 px: three-column listing grids.
- 1280 px and above: four-column listing grids.
- Maps stack controls above the map below 768 px.
- No horizontal page overflow is allowed.

## 8. Accessibility

- Keyboard focus must be visible.
- Images require meaningful alt text or an empty alt for decoration.
- Icon-only buttons require an accessible label.
- Text contrast targets WCAG AA.
- Respect `prefers-reduced-motion`.
- Click targets are at least 44 by 44 px.

## 9. Language

All visible strings must be available in Thai and English. Do not mix languages within one selected locale, except product names such as Petpal AI, Leaflet, and OpenStreetMap. Never store corrupted placeholder text such as question-mark runs.

## 10. Page matrix

- Landing: marketing container, restrained hero, shared stats and card patterns.
- Adoption/Lost lists: list container, filter bar, map, standard pet grid.
- Post detail: content container, image/details card, location card, comments.
- Report create/edit: content container, grouped form cards, location privacy acknowledgement.
- Profile/Pets/My posts: content or marketing container with shared cards and action hierarchy.
- Requests/Chat/AI chat: list or chat workspace standards.
- Contact: content container and organization cards.
- Authentication: shared overlay component.
- Poster and email: print/email-specific layout, but shared brand colors and typography.

## 11. Definition of done

A UI change is complete only when desktop and mobile layouts are checked, horizontal overflow is absent, Thai and English states are reviewed, empty/error/loading states remain readable, keyboard focus is visible, and the Django system check passes.
