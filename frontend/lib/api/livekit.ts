const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

export interface VoiceTokenResponse {
  server_url: string;
  participant_token: string;
  room_name: string;
  participant_identity: string;
}

export async function createVoiceToken(
  participantName?: string,
): Promise<VoiceTokenResponse> {
  const response = await fetch(
    `${API_URL}/voice/token`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        participant_name:
          participantName || "Hospital Patient",
      }),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to create voice session.",
    );
  }

  return response.json();
}