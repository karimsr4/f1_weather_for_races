import { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import { DropdownButton, Dropdown } from 'react-bootstrap'; // Import Dropdown components
import './App.css';
import TimeSeriesChart from './TimeSeriesChart';



function App() {
  const [years, setYears] = useState([]);
  const [races, setRaces] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedRace, setSelectedRace] = useState('');
  const [selectedSession, setSelectedSession] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [dataAvailable, setDataAvailable] = useState(true);
  const apiUrl = process.env.REACT_APP_API_URL;


  useEffect(() => {
    fetchYears(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchYears = async () => {
    try {
      const response = await axios.get(`${apiUrl}/available_years`);
      setYears(response.data.available_years);
    } catch (error) {
      console.error('Error fetching years:', error);
    }
  };

  const fetchRaces = async (year) => {
    try {
      const response = await axios.get(`${apiUrl}/available_races/${year}`);
      setRaces(response.data.available_races);
      setSessions([]);
      setSelectedRace('');
      setSelectedSession('');
      setWeatherData(null);
      setDataAvailable(true);
    } catch (error) {
      console.error('Error fetching races:', error);
    }
  };

  const fetchSessions = async (year, race) => {
    try {
      const response = await axios.get(`${apiUrl}/available_sessions/${year}/${race}`);
      setSessions(response.data.available_sessions);
      setSelectedSession('');
      setWeatherData(null);
      if (response.data.available_sessions.length === 0) {
        setDataAvailable(false);
      } else {
        setDataAvailable(true);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
      setDataAvailable(false);
    }
  };

  const handleYearChange = (year) => {
    setSelectedYear(year);
    fetchRaces(year);
  };

  const handleRaceChange = (race) => {
    setSelectedRace(race);
    fetchSessions(selectedYear, race);
  };

  const handleSessionChange = async (session) => {
    setSelectedSession(session);
    try {
      const response = await axios.get(`${apiUrl}/weather_data/${selectedYear}/${selectedRace}/${session}`);
      if (response.data && response.data.temperature && response.data.temperature.time.length > 0) {
        setWeatherData(response.data);
        setDataAvailable(true);
      } else {
        setWeatherData(null);
        setDataAvailable(false);
      }
    } catch (error) {
      console.error('Error fetching weather data:', error);
      setWeatherData(null);
      setDataAvailable(false);
    }
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Weather variables for F1 races</h1>
      <div className="d-flex justify-content-center mb-4">
        <DropdownButton id="dropdown-year" title={selectedYear ? selectedYear : 'Select Year'} variant="secondary">
          {years.map((year) => (
            <Dropdown.Item key={year} onClick={() => handleYearChange(year)}>{year}</Dropdown.Item>
          ))}
        </DropdownButton>
        <DropdownButton id="dropdown-race" title={selectedRace ? selectedRace : 'Select Race'} variant="secondary" disabled={!selectedYear}>
          {races.map((race) => (
            <Dropdown.Item key={race} onClick={() => handleRaceChange(race)}>{race}</Dropdown.Item>
          ))}
        </DropdownButton>
        <DropdownButton id="dropdown-session" title={sessions.length > 0 ? (selectedSession ? selectedSession : 'Select Session') : 'No Sessions Available'} variant="secondary" disabled={!selectedRace}>
          {sessions.map((session) => (
            <Dropdown.Item key={session} onClick={() => handleSessionChange(session)}>{session}</Dropdown.Item>
          ))}
        </DropdownButton>
      </div>
      {!dataAvailable && (
        <div className="text-center">
          <h4>Data is not available yet for this event.</h4>
        </div>
      )}
      {dataAvailable && weatherData && (
        <>
          <div className="row">
            <div className="col-md-6">
              <TimeSeriesChart title="Temperature" data={weatherData.temperature} unit="°C" start_time={weatherData.start_time} end_time={weatherData.end_time} />
            </div>
            <div className="col-md-6">
              <TimeSeriesChart title="Relative Humidity" data={weatherData.humidity} unit="%" start_time={weatherData.start_time} end_time={weatherData.end_time} />
            </div>
          </div>
          <div className="row">
            <div className="col-md-6">
              <TimeSeriesChart title="Rain" data={weatherData.rain} unit="mm" start_time={weatherData.start_time} end_time={weatherData.end_time} />
            </div>
            <div className="col-md-6">
              <TimeSeriesChart title="Wind Speed" data={weatherData.windSpeed} unit="km/h" start_time={weatherData.start_time} end_time={weatherData.end_time} />
            </div>
          </div>
          <div className="row">
            <div className="col-md-6">
              <TimeSeriesChart title="Wind Direction" data={weatherData.windDirection} unit="°" start_time={weatherData.start_time} end_time={weatherData.end_time} />
            </div>
            <div className="col-md-6">
              <TimeSeriesChart title="Surface Pressure" data={weatherData.pressure} unit="hPa" start_time={weatherData.start_time} end_time={weatherData.end_time} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
