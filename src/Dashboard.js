import './Dashboard.css';
import { useState, useEffect } from 'react';

const handlePing = () => {
    fetch('https://mbs98bg1-5001.use.devtunnels.ms/api/ping')
        .then(res => res.json())
        .then(data => {
            console.log("Ping response:", data.message);
            alert("Backend says: " + data.message); // optional UI feedback
        })
        .catch(err => {
            console.error("Ping failed:", err);
            alert("Failed to connect to backend.");
        });
};
function Dashboard() {
    const [flMask, setFlMask] = useState("/bolts_plus_receipt.JPG");
    const [flImg, setFlImg] = useState("/bolts_plus_receipt.JPG");
    const [frMask, setFrMask] = useState("/bolts_plus_receipt.JPG");
    const [frImg, setFrImg] = useState("/bolts_plus_receipt.JPG");
    const [blMask, setBlMask] = useState("/bolts_plus_receipt.JPG");
    const [blImg, setBlImg] = useState("/bolts_plus_receipt.JPG");
    const [brMask, setBrMask] = useState("/bolts_plus_receipt.JPG");
    const [brImg, setBrImg] = useState("/bolts_plus_receipt.JPG");

    const [timeElapsed, setTimeElapsed] = useState(0);

    // const UpdateDashboard = () => {
    //     // API Call√
    //     fetch('http://localhost:5000/api/update_image_ep', { method: 'PUT' })
    //         .then(res => {
    //             if (!res.ok) {
    //                 throw new Error('Network Error Detected.');
    //             }
    //             return res.json();
    //         })
    //         .then(data => {
    //             setFlImg(data.updatedFLURL + '?t=' + Date.now());
    //             setFrImg(data.updatedFRURL + '?t=' + Date.now());
    //             setBlImg(data.updatedBLURL + '?t=' + Date.now());
    //             setBrImg(data.updatedBRURL + '?t=' + Date.now());
    //         })
    //         .catch(err => {
    //             console.error(`Error uploading image: ${err}`);
    //         });
    // }
    // https://bhf-dashboard.onrender.com/api/update_image_ep
    useEffect(() => {
        const dashboardImgRefresher = setInterval(async () => {
            // https://kl4jx9kg-5000.use.devtunnels.ms
            //await fetch('https://mbs98bg1-5000.use.devtunnels.ms/api/update_image_ep', { method: 'PUT' })
            await fetch('https://mbs98bg1-5001.use.devtunnels.ms/api/update_image_ep', { method: 'PUT'})
                .then(res => {
                    if (!res.ok) {
                        throw new Error('Network Error Detected.');
                    }
                    return res.json();
                })
                .then(data => {
                    setFlImg(data.updatedFLURL);
                    setFrImg(data.updatedFRURL);
                    setBlImg(data.updatedBLURL);
                    setBrImg(data.updatedBRURL);
                    
                    setFlMask(data.flMask);
                    setFrMask(data.frMask);
                    setBlMask(data.blMask);
                    setBrMask(data.brMask);
                })
                .catch(err => {
                    console.error(`Error uploading image: ${err}`);
                });
        }, 1000);

        return () => clearInterval(dashboardImgRefresher);
    }, []);

    useEffect(() => {
        const timeTicker = setInterval(() => {
            setTimeElapsed(timeElapsed => timeElapsed + 1);
        }, 1000);

        return () => clearInterval(timeTicker);
    }, []);
    useEffect(() => {
        fetch('https://mbs98bg1-5001.use.devtunnels.ms/api/ping') // adjust port if needed
        .then(res => res.json())
        .then(data => {
            console.log("Response from backend:", data.message); // should log "pong"
        })
        .catch(err => {
            console.error("Failed to connect to backend:", err);
        });
    }, []);
    return (
        <div className="page">
            <div className='countContainer'>
                <h1 className='timeElapsed'>
                    { Math.floor(timeElapsed / 3600) }:{ String((Math.floor(timeElapsed / 60)) % 60).padStart(2, "0") }:{String(timeElapsed % 60).padStart(2, "0")}
                </h1>
            </div>
            <div className="imgContainer">
                <div className='row'>
                    <div className='camImg'>
                        <p>Front Left</p>
                        <div className='flImgs'>
                            <img src={flMask} className="flMask" alt="Current processed mask overlay from the front left" width={300}/>
                            <img src={flImg} className="flImg" alt="Current processed feed from the front left camera of the robot" width={300}/>
                        </div>
                    </div>
                    <div className='camImg'>
                        <p>Front Right</p>
                        <div className='frImgs'>
                            <img src={frImg} className="frImg" alt="Current processed feed from the front right camera of the robot" width={300} />
                            <img src={frMask} className="frMask" alt="Current processed mask overlay from the front right" width={300}/>
                        </div>
                    </div>
                </div>
                <div className='row'>
                    <div className='camImg'>
                        <p>Back Left</p>
                        <div className='blImgs'>
                            <img src={blMask} className="blMask" alt="Current processed mask overlay from the front right" width={300}/>
                            <img src={blImg} className="blImg" alt="Current processed feed from the back left camera of the robot" width={300}/>
                        </div>
                    </div>
                    <div className='camImg'>
                        <p>Back Right</p>
                        <div className='brImgs'>
                            <img src={brImg} className="brImg" alt="Current processed feed from the back right camera of the robot" width={300} />
                            <img src={brMask} className="brMask" alt="Current processed mask overlay from the front right" width={300}/>
                        </div>
                    </div>
                </div>
            </div>
            <div className="pingButtonContainer">
                <button className="pingButton" onClick={handlePing}>PLEASE JUST PONG BACK</button>
            </div>
            {/* <div className="updateImgBtnContainer">
                <button className="updateImgBtn" onClick={UpdateDashboard}>Update Dashboard</button>
            </div> */}
        </div>
    );
}

export default Dashboard;