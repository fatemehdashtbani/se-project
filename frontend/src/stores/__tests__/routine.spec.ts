import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useRoutineStore, type Routine } from '../routine';

const ROUTINE: Routine = {
  id: '3f4a0d90-1b2c-4d3e-8f5a-6b7c8d9e0f1a',
  title: 'صبحانه',
  description: 'هر روز صبح ساعت ۷',
  is_active: true,
  created_at: '2026-11-24T06:00:00Z',
  updated_at: '2026-11-24T06:00:00Z',
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

describe('useRoutineStore (F-005)', () => {
  it('fetchRoutines() loads the caller\'s routines from the list endpoint', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { items: [ROUTINE], total: 1 }));

    const store = useRoutineStore();
    await store.fetchRoutines();

    expect(store.routines).toEqual([ROUTINE]);
    expect(store.isLoading).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/routines',
      expect.objectContaining({ method: 'GET', credentials: 'include' }),
    );
  });

  it('fetchRoutines() clears isLoading and keeps existing routines on failure', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(401, { error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } }),
    );

    const store = useRoutineStore();
    store.$patch({ routines: [ROUTINE] });

    await expect(store.fetchRoutines()).rejects.toMatchObject({ status: 401 });
    expect(store.routines).toEqual([ROUTINE]);
    expect(store.isLoading).toBe(false);
  });

  it('createRoutine() posts the payload and appends the created routine', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, ROUTINE));

    const store = useRoutineStore();
    await store.createRoutine('صبحانه', 'هر روز صبح ساعت ۷');

    expect(store.routines).toEqual([ROUTINE]);
    expect(store.isLoading).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/routines',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ title: 'صبحانه', description: 'هر روز صبح ساعت ۷' }),
      }),
    );
  });

  it('createRoutine() does not append anything when the request fails', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(422, { error: { code: 'VALIDATION_ERROR', message: 'Invalid' } }),
    );

    const store = useRoutineStore();

    await expect(store.createRoutine('', null)).rejects.toMatchObject({ status: 422 });
    expect(store.routines).toEqual([]);
    expect(store.isLoading).toBe(false);
  });

  it('updateRoutine() puts the edit and replaces only that routine', async () => {
    const otherRoutine = { ...ROUTINE, id: 'another-id', title: 'ورزش' };
    const updated = { ...ROUTINE, title: 'صبحانه سالم', description: null };
    const store = useRoutineStore();
    store.$patch({ routines: [ROUTINE, otherRoutine] });
    fetchMock.mockResolvedValueOnce(jsonResponse(200, updated));

    await store.updateRoutine(ROUTINE.id, 'صبحانه سالم', null);

    expect(store.routines).toEqual([updated, otherRoutine]);
    expect(store.isLoading).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/v1/routines/${ROUTINE.id}`,
      expect.objectContaining({
        method: 'PUT',
        credentials: 'include',
        body: JSON.stringify({ title: 'صبحانه سالم', description: null }),
      }),
    );
  });

  it('updateRoutine() keeps the list untouched when the request fails', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(404, { error: { code: 'ROUTINE_NOT_FOUND', message: 'Missing' } }),
    );

    const store = useRoutineStore();
    store.$patch({ routines: [ROUTINE] });

    await expect(store.updateRoutine(ROUTINE.id, 'x', null)).rejects.toMatchObject({
      status: 404,
    });
    expect(store.routines).toEqual([ROUTINE]);
    expect(store.isLoading).toBe(false);
  });

  it('deleteRoutine() removes only the deleted routine', async () => {
    const otherRoutine = { ...ROUTINE, id: 'another-id', title: 'ورزش' };
    const store = useRoutineStore();
    store.$patch({ routines: [ROUTINE, otherRoutine] });
    fetchMock.mockResolvedValueOnce(jsonResponse(204, undefined));

    await store.deleteRoutine(ROUTINE.id);

    expect(store.routines).toEqual([otherRoutine]);
    expect(store.isLoading).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/v1/routines/${ROUTINE.id}`,
      expect.objectContaining({ method: 'DELETE', credentials: 'include' }),
    );
  });
});
