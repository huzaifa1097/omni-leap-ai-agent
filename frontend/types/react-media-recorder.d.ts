declare module 'react-media-recorder' {
  import * as React from 'react';

  type Status = 'idle' | 'recording' | 'stopped' | 'acquiring_media';

  interface ReactMediaRecorderProps {
    audio?: boolean | any;
    video?: boolean | any;
    screen?: boolean;
    onStop?: (blobUrl: string, blob: Blob) => void;
    blobPropertyBag?: BlobPropertyBag;
    mediaRecorderOptions?: MediaRecorderOptions;
  }

  interface ReactMediaRecorderRenderProps {
    status: Status;
    startRecording: () => void;
    stopRecording: () => void;
    mediaBlobUrl: string | null;
    previewStream: MediaStream | null;
  }

  export const useReactMediaRecorder: (props: ReactMediaRecorderProps) => ReactMediaRecorderRenderProps;

  export class ReactMediaRecorder extends React.Component<ReactMediaRecorderProps> {
    render(): React.ReactElement<ReactMediaRecorderRenderProps>;
  }
}