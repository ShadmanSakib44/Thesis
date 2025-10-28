import Likert from './Likert';

interface Props {
  story: string;
  ratings: number[];
  setRatings: (aspectIdx: number, value: number) => void;
  disabled?: boolean;
}

const labels = ['Readability', 'Understandability', 'Specifyability', 'Technical Aspects'];

export default function UserStoryBlock({ story, ratings, setRatings, disabled = false }: Props) {
  return (
    <div className={`border p-4 rounded shadow-md ${disabled ? 'bg-gray-100 opacity-50' : 'bg-white'}`}>
      <p className="mb-4 font-medium">{story || <em>No user story available.</em>}</p>
      {labels.map((label, i) => (
        <Likert
          key={label}
          label={label}
          value={ratings[i]}
          onChange={(v) => setRatings(i, v)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}
