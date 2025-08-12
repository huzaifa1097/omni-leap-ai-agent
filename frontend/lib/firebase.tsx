import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAdJuSVgTtgknW6gy1H2WeLGwNcetyHHY4",
  authDomain: "omni-client-21d02.firebaseapp.com",
  projectId: "omni-client-21d02",
  storageBucket: "omni-client-21d02.appspot.com",
  messagingSenderId: "159570946595",
  appId: "1:159570946595:web:76edd37e41838261085f96",
  measurementId: "G-WCW24GDD5Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize and EXPORT Firebase Authentication
export const auth = getAuth(app);
