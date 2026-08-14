const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export interface AppointmentSlot {
  id: string;
  doctor_id: string;
  specialization?: string;
  slot_date: string;
  start_time: string;
  end_time?: string;
  is_available: boolean;
}

export interface BookAppointmentRequest {
  patient_id: string;
  slot_id: string;
  reason?: string;
}

export async function getAppointmentSlots(params?: {
  specialization?: string;
  date_from?: string;
  limit?: number;
}): Promise<AppointmentSlot[]> {
  const searchParams = new URLSearchParams();

  if (params?.specialization) {
    searchParams.set(
      "specialization",
      params.specialization,
    );
  }

  if (params?.date_from) {
    searchParams.set(
      "date_from",
      params.date_from,
    );
  }

  if (params?.limit) {
    searchParams.set(
      "limit",
      String(params.limit),
    );
  }

  const query = searchParams.toString();

  const url = query
    ? `${API_URL}/appointments/slots?${query}`
    : `${API_URL}/appointments/slots`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to load available appointment slots.",
    );
  }

  return response.json();
}

export async function bookAppointment(
  data: BookAppointmentRequest,
) {
  const response = await fetch(
    `${API_URL}/appointments`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(data),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to book appointment.",
    );
  }

  return response.json();
}

export async function cancelAppointment(
  appointmentId: string,
  patientId: string,
) {
  const response = await fetch(
    `${API_URL}/appointments/${appointmentId}/cancel?patient_id=${patientId}`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to cancel appointment.",
    );
  }

  return response.json();
}