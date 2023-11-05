# spotipyApp

Spotify Playlist Curator

This web application harnesses the power of the Spotify API to create a personalized listening experience. Built with Python and Flask, it offers a seamless integration with users' Spotify accounts, maintaining security and privacy through OAuth authentication protocols.

Key Features:

- ## OAuth Authentication: 
Implements OAuth 2.0 to securely connect with Spotify accounts, ensuring that user credentials are protected while allowing the application to interact with Spotify data on their behalf.

- ## Personalized Playlists: 
Provides users with the ability to generate playlists in a variety of ways:

  - Based on their top 25 most-played songs.
  - Reflecting their top 5 tracks over the last month.
  - Curated from their top 5 favorite artists.

- ## Song Recommendation Algorithm:
-   At the heart of the application is a sophisticated song recommendation system, crafted in Python. It utilizes:

  - Pandas for efficient data management and analysis, handling complex data operations to match user preferences.
  - Matplotlib and Seaborn for generating interactive plots. These plots not only provide a visual representation of the songs' data points but also highlight the selections that best match the user's input.
- ## Custom User Inputs: Users can define their current mood by setting values for 'danceability', 'energy', and 'valence' on a scale from 1 to 10. This nuanced approach allows for a more personalized and responsive playlist creation process.

- ## Data Visualization: The app features a sophisticated visualization component that graphs the characteristics of various songs, comparing them with the user's mood inputs. The visualization assists users in understanding why certain songs were recommended and how they relate to the specified parameters.

- ## Algorithmic Matching: Leveraging a custom-built similarity scoring system, the app analyzes the audio features of songs to find the best matches for the user's mood criteria. The top 10 recommendations are presented, giving users new and exciting songs to explore and enjoy.

## Technologies Used:

- Backend: Python, Flask
- Data Analysis and Algorithm: Pandas (for data manipulation), Python (for algorithm development)
- Data Visualization: Matplotlib, Seaborn (for generating interactive plots)
- API Integration: Spotify API
- Authentication: OAuth 2.0 for secure access to user data
