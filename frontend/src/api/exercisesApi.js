// src/api/exercisesApi.js

export async function uploadToDjango(audioBlob, exerciseId) {
  // 1. You CANNOT use standard JSON for files. We must use FormData.
  const formData = new FormData();

  // 2. Append the file. We name it 'audio_file' to match our Django Serializer!
  formData.append("audio_file", audioBlob, "recording.webm");

  // 3. Append the exercise ID
  formData.append("exercise", exerciseId);

  // 4. Grab the JWT token from LocalStorage
  const token = localStorage.getItem("access_token");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/exercises/attempts/",
      {
        method: "POST",
        headers: {
          // Notice we do NOT set 'Content-Type: application/json'
          // The browser automatically sets the correct multipart boundary for FormData!
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      },
    );

    const data = await response.json();
    console.log("AI Analysis Complete!", data);

    // It's good practice to return the data so your React component can use it (e.g., to show the score)
    return data;
  } catch (error) {
    console.error("Upload failed", error);
    throw error;
  }
}
