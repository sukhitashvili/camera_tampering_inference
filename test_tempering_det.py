import argparse

import cv2

from core.detect_tampering import TamperingDetector


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key_frame_path', required=True, type=str,
                        help='Key frame file path')
    parser.add_argument('--video_path', required=True, type=str,
                        help='Video file path to test tempering detection algorithm')
    args = parser.parse_args()
    return args


def main(key_frame_path, video_path):
    tampering_detector = TamperingDetector(run_every_nth=1,
                                           key_frame_path=key_frame_path)
    vid_cap = cv2.VideoCapture(video_path)
    if not vid_cap.isOpened():
        raise RuntimeError("Error opening video stream or file")

    while vid_cap.isOpened():
        ret, frame = vid_cap.read()
        if ret:
            prediction = tampering_detector.inference(frame=frame)
            if prediction:
                text = 'Tampering'
                cv2.putText(frame, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                text = 'Normal'
                cv2.putText(frame, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow('Frame', frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        else:
            break

    # When everything done, release the video capture object
    vid_cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()


if __name__ == "__main__":
    args = get_args()
    main(key_frame_path=args.key_frame_path, video_path=args.video_path)
