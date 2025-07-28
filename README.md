Major project with video calling feature,screen sharing and video upload feature. 
Video Calling --> In which the sign language user can communicate using sign language as it is convert into captions so anyone can understand and communicate.  
Video Upload  --> Uploaded video is captioned using KNN model and the caption is also converted to audio in multi-lingual speech (hindi,marathi and english)

SETUP :
1.Clone repo
2.run node server, nodemon server.js
3.run python server,cd server python app.py (make sure the model.pkl in dir path is correctif any error occ)
4.use ngrok for another user to be connected on socket for video call --> ngrok http 9000 as node server is running on 9000
5.that link from ngrok ( ??link.free.app --> open on any device/mobile and give any name to it and join video call)

gg
