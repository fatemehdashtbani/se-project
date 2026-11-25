import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useChecklistStore, type ChecklistItem } from '../checklist';
import { useNoteStore, type Note } from '../notes';
import { useCalendarStore, type CalendarEvent } from '../calendar';

const CHECKLIST_ITEM: ChecklistItem = {
  id: '11111111-1111-4111-8111-111111111111',
  title: 'خرید نان',
  is_done: false,
  created_at: '2026-11-25T08:00:00Z',
  updated_at: '2026-11-25T08:00:00Z',
};

const NOTE: Note = {
  id: '22222222-2222-4222-8222-222222222222',
  title: 'ایده',
  content: 'متن',
  created_at: '2026-11-25T08:00:00Z',
  updated_at: '2026-11-25T08:00:00Z',
};

const EVENT: CalendarEvent = {
  id: '33333333-3333-4333-8333-333333333333',
  title: 'جلسه',
  event_date: '2026-12-10',
  event_time: null,
  created_at: '2026-11-25T08:00:00Z',
};

let fetchMock: ReturnType<typeof vi.fn>;

function jsonResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as unknown as Response;
}

beforeEach(() => {
  setActivePinia(createPinia());
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('useChecklistStore (F-033)', () => {
  it('fetchItems() loads the checklist', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, { items: [CHECKLIST_ITEM], total: 1, done: 0 }),
    );

    const store = useChecklistStore();
    await store.fetchItems();

    expect(store.items).toEqual([CHECKLIST_ITEM]);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/checklist-items',
      expect.objectContaining({ method: 'GET', credentials: 'include' }),
    );
  });

  it('createItem() appends the created item', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, CHECKLIST_ITEM));

    const store = useChecklistStore();
    await store.createItem('خرید نان');

    expect(store.items).toEqual([CHECKLIST_ITEM]);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/checklist-items',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ title: 'خرید نان' }),
      }),
    );
  });

  it('setDone() replaces only the toggled item', async () => {
    const other = { ...CHECKLIST_ITEM, id: 'another-id', title: 'ورزش' };
    const done = { ...CHECKLIST_ITEM, is_done: true };
    const store = useChecklistStore();
    store.$patch({ items: [CHECKLIST_ITEM, other] });
    fetchMock.mockResolvedValueOnce(jsonResponse(200, done));

    await store.setDone(CHECKLIST_ITEM.id, true);

    expect(store.items).toEqual([done, other]);
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/v1/checklist-items/${CHECKLIST_ITEM.id}`,
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({ is_done: true }),
      }),
    );
  });

  it('deleteItem() removes only the deleted item and keeps the list on failure', async () => {
    const other = { ...CHECKLIST_ITEM, id: 'another-id' };
    const store = useChecklistStore();
    store.$patch({ items: [CHECKLIST_ITEM, other] });
    fetchMock.mockResolvedValueOnce(jsonResponse(204, undefined));

    await store.deleteItem(CHECKLIST_ITEM.id);
    expect(store.items).toEqual([other]);

    fetchMock.mockResolvedValueOnce(
      jsonResponse(500, { error: { code: 'HTTP_ERROR', message: 'Boom' } }),
    );
    await expect(store.deleteItem(other.id)).rejects.toMatchObject({ status: 500 });
    expect(store.items).toEqual([other]);
    expect(store.isLoading).toBe(false);
  });
});

describe('useNoteStore (F-033)', () => {
  it('fetchNotes() loads the notes', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { items: [NOTE], total: 1 }));

    const store = useNoteStore();
    await store.fetchNotes();

    expect(store.notes).toEqual([NOTE]);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/notes',
      expect.objectContaining({ method: 'GET' }),
    );
  });

  it('createNote() prepends the server representation', async () => {
    const store = useNoteStore();
    store.$patch({ notes: [{ ...NOTE, id: 'older-id' }] });
    fetchMock.mockResolvedValueOnce(jsonResponse(201, NOTE));

    await store.createNote('ایده', 'متن');

    expect(store.notes).toEqual([NOTE, { ...NOTE, id: 'older-id' }]);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/notes',
      expect.objectContaining({ body: JSON.stringify({ title: 'ایده', content: 'متن' }) }),
    );
  });

  it('updateNote() replaces the edited note', async () => {
    const edited = { ...NOTE, title: 'ایده جدید', content: 'متن دوم' };
    const store = useNoteStore();
    store.$patch({ notes: [NOTE] });
    fetchMock.mockResolvedValueOnce(jsonResponse(200, edited));

    await store.updateNote(NOTE.id, 'ایده جدید', 'متن دوم');

    expect(store.notes).toEqual([edited]);
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/v1/notes/${NOTE.id}`,
      expect.objectContaining({ method: 'PUT' }),
    );
  });

  it('deleteNote() drops the note after the delete succeeds', async () => {
    const store = useNoteStore();
    store.$patch({ notes: [NOTE] });
    fetchMock.mockResolvedValueOnce(jsonResponse(204, undefined));

    await store.deleteNote(NOTE.id);

    expect(store.notes).toEqual([]);
    expect(store.isLoading).toBe(false);
  });
});

describe('useCalendarStore (F-033)', () => {
  it('fetchEvents() loads every event', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { items: [EVENT], total: 1 }));

    const store = useCalendarStore();
    await store.fetchEvents();

    expect(store.events).toEqual([EVENT]);
  });

  it('createEvent() posts the date and keeps the list sorted', async () => {
    const later = { ...EVENT, id: 'later-id', event_date: '2027-01-01' };
    const store = useCalendarStore();
    store.$patch({ events: [later] });
    fetchMock.mockResolvedValueOnce(jsonResponse(201, EVENT));

    await store.createEvent('جلسه', '2026-12-10');

    expect(store.events).toEqual([EVENT, later]);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/calendar-events',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ title: 'جلسه', event_date: '2026-12-10' }),
      }),
    );
  });

  it('deleteEvent() removes the deleted event', async () => {
    const store = useCalendarStore();
    store.$patch({ events: [EVENT] });
    fetchMock.mockResolvedValueOnce(jsonResponse(204, undefined));

    await store.deleteEvent(EVENT.id);

    expect(store.events).toEqual([]);
  });

  it('createEvent() sends the time only when one is set', async () => {
    const timed = { ...EVENT, event_time: '14:30:00' };
    const store = useCalendarStore();
    fetchMock.mockResolvedValueOnce(jsonResponse(201, timed));

    await store.createEvent('جلسه', '2026-12-10', '14:30');

    expect(store.events).toEqual([timed]);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/calendar-events',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ title: 'جلسه', event_date: '2026-12-10', event_time: '14:30' }),
      }),
    );
  });
});
