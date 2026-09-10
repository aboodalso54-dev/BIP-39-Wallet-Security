import React from 'react';
// SafeAreaView is deprecated in newer RN versions; consider migrating to react-native-safe-area-context
import { SafeAreaView, Text } from 'react-native';

const MyApp = () => {
  return (
    <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Hello, World!</Text>
    </SafeAreaView>
  );
};

export default MyApp;