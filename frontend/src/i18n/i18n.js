import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Multilingual support: English + Hindi (architecture ready for more
// Indian languages — just add another resource block below).
const resources = {
  en: {
    translation: {
      appName: 'KisanDirect',
      tagline: 'Sell direct. Earn fair. Grow together.',
      login: 'Login',
      register: 'Register',
      farmer: 'Farmer',
      buyer: 'Buyer',
      dashboard: 'Dashboard',
      addCrop: 'Add Crop Listing',
      myListings: 'My Listings',
      offers: 'Offers',
      orders: 'Orders',
      marketplace: 'Marketplace',
      priceIntelligence: 'Price Intelligence',
      demandForecast: 'Demand Forecast',
      logistics: 'Logistics',
      aiRecommendation: 'AI Recommendation',
      bestBuyerRecommendation: 'Best buyer recommendation',
      payments: 'Payments',
      adminDashboard: 'Admin Dashboard',
      logout: 'Logout',
      crop: 'Crop', quantity: 'Quantity (kg)', quality: 'Quality Grade',
      expectedPrice: 'Expected Price (₹/kg)', harvestDate: 'Harvest Date',
      location: 'Location', submit: 'Submit', acceptOffer: 'Accept Offer',
      makeOffer: 'Make Offer', matchScore: 'Match Score',
    },
  },
  hi: {
    translation: {
      appName: 'किसानडायरेक्ट',
      tagline: 'सीधे बेचें। उचित कमाएं। साथ बढ़ें।',
      login: 'लॉगिन',
      register: 'पंजीकरण करें',
      farmer: 'किसान',
      buyer: 'खरीदार',
      dashboard: 'डैशबोर्ड',
      addCrop: 'फसल जोड़ें',
      myListings: 'मेरी सूची',
      offers: 'प्रस्ताव',
      orders: 'ऑर्डर',
      marketplace: 'बाज़ार',
      priceIntelligence: 'मूल्य जानकारी',
      demandForecast: 'मांग पूर्वानुमान',
      logistics: 'रसद',
      aiRecommendation: 'AI सुझाव',
      bestBuyerRecommendation: 'सबसे अच्छा खरीदार सुझाव',
      payments: 'भुगतान',
      adminDashboard: 'व्यवस्थापक डैशबोर्ड',
      logout: 'लॉगआउट',
      crop: 'फसल', quantity: 'मात्रा (किग्रा)', quality: 'गुणवत्ता ग्रेड',
      expectedPrice: 'अपेक्षित मूल्य (₹/किग्रा)', harvestDate: 'कटाई की तारीख',
      location: 'स्थान', submit: 'जमा करें', acceptOffer: 'प्रस्ताव स्वीकारें',
      makeOffer: 'प्रस्ताव दें', matchScore: 'मिलान स्कोर',
    },
  },
}

i18n.use(initReactI18next).init({
  resources,
  lng: localStorage.getItem('kd_lang') || 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
